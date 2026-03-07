from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.frames.frames import LLMMessagesAppendFrame
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMAssistantAggregatorParams,
    LLMContextAggregatorPair,
    LLMUserAggregator,
    LLMUserAggregatorParams,
)
from pipecat.services.nvidia.llm import NvidiaLLMService
from pipecat.services.nvidia.stt import NvidiaSTTService
from pipecat.services.nvidia.tts import NvidiaTTSService as _NvidiaTTSService
from pipecat.transcriptions.language import Language
from pipecat.turns.user_mute import FirstSpeechUserMuteStrategy
from pipecat.turns.user_start import (
    TranscriptionUserTurnStartStrategy,
    VADUserTurnStartStrategy,
)
from pipecat.turns.user_stop import TurnAnalyzerUserTurnStopStrategy
from pipecat.turns.user_turn_strategies import UserTurnStrategies

from app.core.secrets import Settings
from app.core.types import ContextAggregatorBundle
from app.pipeline.config import BotConfig


class NvidiaTTSService(_NvidiaTTSService):
    def can_generate_metrics(self) -> bool:
        return True


class PipecatServiceFactory:
    def __init__(self, secrets: Settings, bot_config: BotConfig):
        self.secrets = secrets
        self.config = bot_config

    def create_stt(self) -> NvidiaSTTService:
        # NOTE: Only en-US works on the NVCF hosted endpoint for both streaming and offline modes.
        # fr-FR, es-ES and other languages are rejected with INVALID_ARGUMENT by NVIDIA's cloud.
        # Root cause: NVIDIA's NVCF endpoint truncates "fr-FR" to "fr" internally and fails to find
        # a matching model — this is NOT a pipecat bug. Confirmed via raw gRPC test that bypasses
        # pipecat entirely (see tests/test_nvidia_asr_all_languages.py). To use other languages,
        # you would need to self-host the NIM container (nvcr.io/nim/nvidia/parakeet-1-1b-rnnt-multilingual).
        stt = NvidiaSTTService(
            api_key=self.secrets.nvidia_api_key,
        )

        return stt

    def create_tts(self) -> NvidiaTTSService:
        tts = NvidiaTTSService(
            api_key=self.secrets.nvidia_api_key,
            voice_id="Magpie-Multilingual.EN-US.Isabela",  # https://docs.nvidia.com/nim/riva/tts/latest/support-matrix.html
            params=NvidiaTTSService.InputParams(language=Language.EN_US, quality=60),
        )

        return tts

    def create_agent(self) -> NvidiaLLMService:
        agent = NvidiaLLMService(
            api_key=self.secrets.nvidia_api_key,
            model="meta/llama-3.3-70b-instruct",
        )
        return agent

    def create_context_agg(self):
        context = LLMContext([{"role": "system", "content": self.config.system_prompt}])
        pair = LLMContextAggregatorPair(
            context=context,
            user_params=LLMUserAggregatorParams(
                vad_analyzer=SileroVADAnalyzer(),
                user_turn_strategies=UserTurnStrategies(
                    start=[
                        VADUserTurnStartStrategy(),
                        TranscriptionUserTurnStartStrategy(),
                    ],
                    stop=[
                        TurnAnalyzerUserTurnStopStrategy(
                            turn_analyzer=LocalSmartTurnAnalyzerV3(cpu_count=2)
                        )
                    ],
                ),
                user_mute_strategies=[FirstSpeechUserMuteStrategy()],
                user_idle_timeout=60,
            ),
            assistant_params=LLMAssistantAggregatorParams(),
        )

        @pair.user().event_handler("on_user_turn_idle")
        async def hook_user(aggregator: LLMUserAggregator):
            await aggregator.push_frame(
                LLMMessagesAppendFrame(
                    messages=[
                        {
                            "role": "user",
                            "content": "The user has been idle. Gently remind them you're here to help.",
                        }
                    ],
                    run_llm=True
                )
            )

        return ContextAggregatorBundle(pair, context)
