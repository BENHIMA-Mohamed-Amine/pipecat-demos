from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import Runnable
from loguru import logger
from pipecat.frames.frames import (
    Frame,
    InputAudioRawFrame,
    LLMContextFrame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
    UserSpeakingFrame,
)
from pipecat.metrics.metrics import LLMTokenUsage
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

# from pipecat.processors.frameworks.langchain import LangchainProcessor


class LangchainProcessor(FrameProcessor):
    def __init__(self, agent: Runnable, thread_id: str):
        super().__init__()
        self._agent = agent
        self._thread_id = thread_id
        self._agent_config = {"configurable": {"thread_id": self._thread_id}}

    def can_generate_metrics(self) -> bool:
        """Check if this processor can generate metrics.

        Returns:
            True if this processor can generate metrics.
        """
        return True

    async def process_frame(self, frame: Frame, direction: FrameDirection):
        await super().process_frame(frame, direction)
        # if not isinstance(frame, (InputAudioRawFrame, UserSpeakingFrame)):
        #     logger.debug(f"frame type: {type(frame)}")
        #     logger.debug(f"frame content: {frame}")

        if isinstance(frame, LLMContextFrame):
            logger.debug(f"Got transcription frame {frame}")
            messages = frame.context.messages
            last_message: str = messages[-1]["content"]
            await self._ainvoke(last_message.strip())
        else:
            await self.push_frame(frame, direction)

    async def _ainvoke(self, text: str):
        logger.debug(f"Invoking agent with {text}")
        await self.push_frame(LLMFullResponseStartFrame())
        await self.start_ttfb_metrics()
        await self.start_processing_metrics()
        first_chunk = True
        try:
            input_data = {"messages": [{"role": "human", "content": text}]}
            async for chunk in self._agent.astream(
                input_data, self._agent_config, mode="updates"
            ):
                for node_name, node_data in chunk.items():
                    messages = node_data.get("messages", [])
                    if not messages:
                        continue
                    last_message = messages[-1]

                    if first_chunk:
                        await self.stop_ttfb_metrics()
                        first_chunk = False

                    if isinstance(last_message, ToolMessage):
                        logger.debug(
                            f"Tool result from {node_name}: {last_message.content[:100]}"
                        )
                        continue

                    if isinstance(last_message, AIMessage):
                        usage = last_message.usage_metadata
                        if usage and usage.get("output_tokens"):
                            tokens = LLMTokenUsage(
                                prompt_tokens=usage.get("input_tokens", 0),
                                completion_tokens=usage.get("output_tokens", 0),
                                total_tokens=usage.get("total_tokens", 0),
                            )
                            await self.start_llm_usage_metrics(tokens)

                        if last_message.content:
                            await self.push_frame(LLMTextFrame(last_message.content))

        except Exception as e:
            await self.push_error(error_msg="Unknown error occurred", exception=e)
        finally:
            await self.stop_ttfb_metrics()
            await self.stop_processing_metrics()
            await self.push_frame(LLMFullResponseEndFrame())
