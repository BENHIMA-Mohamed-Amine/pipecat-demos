from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver

from app.core.secrets import Settings


@dataclass
class AgentConfig:
    system_prompt: str = """
You are a warm and knowledgeable Moroccan travel guide who helps travelers
discover Morocco's cities, monuments, hidden gems, and cultural customs — always responding in short sentences, maximum 2 sentences. Always respond in English regardless of the language of the input.
    """


class LangchainAgent:
    def __init__(self, secrets: Settings):
        self._model = ChatGroq(
            model="openai/gpt-oss-120b", api_key=secrets.groq_api_key
        )
        self._checkpointer = InMemorySaver()
        self._agent_config = AgentConfig()

    def create(self):
        return create_agent(
            model=self._model,
            system_prompt=self._agent_config.system_prompt,
            checkpointer=self._checkpointer,
        )
