from dataclasses import dataclass

from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
)


@dataclass
class ContextAggregatorBundle:
    pair: LLMContextAggregatorPair
    context: LLMContext
