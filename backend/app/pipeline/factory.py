from langchain_core.runnables import Runnable
from pipecat.audio.turn.smart_turn.base_smart_turn import SmartTurnParams
from pipecat.audio.turn.smart_turn.local_smart_turn_v3 import LocalSmartTurnAnalyzerV3
from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMAssistantAggregatorParams,
    LLMContextAggregatorPair,
    LLMUserAggregatorParams,
)
from pipecat.services.nvidia.stt import NvidiaSegmentedSTTService, NvidiaSTTService
from pipecat.services.nvidia.tts import NvidiaTTSService as _NvidiaTTSService
from pipecat.transcriptions.language import Language
from pipecat.turns.user_start import (
    TranscriptionUserTurnStartStrategy,
    VADUserTurnStartStrategy,
)
from pipecat.turns.user_stop import TurnAnalyzerUserTurnStopStrategy
from pipecat.turns.user_turn_strategies import UserTurnStrategies

from app.core.secrets import Settings
from app.core.types import ContextAggregatorBundle
from app.services.langchain_processor import LangchainProcessor


class NvidiaTTSService(_NvidiaTTSService):
    def can_generate_metrics(self) -> bool:
        return True


class PipecatServiceFactory:
    def __init__(self, secrets: Settings):
        self.secrets = secrets

    def create_stt(self) -> NvidiaSegmentedSTTService:

        stt = NvidiaSTTService(
            api_key=self.secrets.nvidia_api_key,
            params=NvidiaSTTService.InputParams(language=Language.EN_US),
        )

        return stt

    def create_tts(self) -> NvidiaTTSService:
        tts = NvidiaTTSService(
            api_key=self.secrets.nvidia_api_key,
            voice_id="Magpie-Multilingual.EN-US.Isabela",  # https://docs.nvidia.com/nim/riva/tts/latest/support-matrix.html
            params=NvidiaTTSService.InputParams(language=Language.EN_US, quality=60),
        )

        return tts

    def create_agent(self, agent: Runnable, thread_id: str) -> LangchainProcessor:
        react_agent = LangchainProcessor(agent, thread_id)
        return react_agent

    def create_context_agg(self):
        context = LLMContext()
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
                            turn_analyzer=LocalSmartTurnAnalyzerV3(
                                cpu_count=2, params=SmartTurnParams(stop_secs=1)
                            )
                        )
                    ],
                ),
                # user_mute_strategies=[FirstSpeechUserMuteStrategy()],
                user_idle_timeout=120,
            ),
            assistant_params=LLMAssistantAggregatorParams(),
        )

        return ContextAggregatorBundle(pair, context)
