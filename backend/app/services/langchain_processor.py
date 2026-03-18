from langchain_core.messages import AIMessage, AIMessageChunk, ToolMessage
from langchain_core.runnables import Runnable
from loguru import logger
from pipecat.frames.frames import (
    Frame,
    InputAudioRawFrame,
    LLMContextFrame,
    LLMFullResponseEndFrame,
    LLMFullResponseStartFrame,
    LLMTextFrame,
    OutputTransportMessageFrame,
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
            async for message, metadata in self._agent.astream(
                input_data, self._agent_config, stream_mode="messages"
            ):
                if isinstance(message, AIMessageChunk) and message.tool_call_chunks:
                    for chunk in message.tool_call_chunks:
                        if chunk.get("name"):
                            logger.info(f"🔧 Tool call: {chunk['name']}")
                            await self.push_frame(
                                OutputTransportMessageFrame(
                                    message={
                                        "label": "rtvi-ai",
                                        "type": "server-message",
                                        "data": {
                                            "event": "tool-call-start",
                                            "tool": chunk["name"],
                                        },
                                    }
                                )
                            )

                if isinstance(message, ToolMessage):
                    logger.info(f"📦 Tool result: {message.content[:100]}")
                    await self.push_frame(
                        OutputTransportMessageFrame(
                            message={
                                "label": "rtvi-ai",
                                "type": "server-message",
                                "data": {
                                    "event": "tool-call-result",
                                    "content": message.content[:300],
                                },
                            }
                        )
                    )
                    continue

                if isinstance(message, AIMessageChunk):
                    if first_chunk and message.content:
                        await self.stop_ttfb_metrics()
                        first_chunk = False

                    if message.content:
                        logger.debug(f"[CHUNK] {repr(message.content)}")
                        await self.push_frame(LLMTextFrame(message.content))

                    usage = message.usage_metadata
                    if usage and usage.get("output_tokens"):
                        tokens = LLMTokenUsage(
                            prompt_tokens=usage.get("input_tokens", 0),
                            completion_tokens=usage.get("output_tokens", 0),
                            total_tokens=usage.get("total_tokens", 0),
                        )
                        await self.start_llm_usage_metrics(tokens)

        except Exception as e:
            logger.exception(f"LangchainProcessor error: {e}")
            await self.push_error(error_msg="Unknown error occurred", exception=e)
        finally:
            await self.stop_ttfb_metrics()
            await self.stop_processing_metrics()
            await self.push_frame(LLMFullResponseEndFrame())
