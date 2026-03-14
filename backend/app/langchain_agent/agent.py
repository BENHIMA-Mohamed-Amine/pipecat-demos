from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_core.tools import BaseTool
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langgraph.checkpoint.memory import InMemorySaver

from app.core.secrets import Settings


@dataclass
class AgentConfig:
    system_prompt: str = """
You are a friendly and knowledgeable consultant for NovaMark Digital, a full-service digital marketing agency.
Your role is to answer questions about NovaMark Digital's services, pricing, and processes.
Always use the retriever_tool to search the knowledge base before answering any question about services, pricing, or processes.
Keep your answers concise — 1 to 2 sentences maximum, with proper punctuation. Be conversational, warm, and professional.
If you cannot find a relevant answer in the knowledge base, invite the caller to book a free discovery call.
Always respond in English regardless of the language of the input.
    """


class LangchainAgent:
    def __init__(self, secrets: Settings, tools: list[BaseTool] | None = None):
        self._model = ChatNVIDIA(
            model="moonshotai/kimi-k2-instruct",
            api_key=secrets.nvidia_api_key,
            top_p=0.9,
            temperature=0.5,
            model_kwargs={
                "presence_penalty": 0.5,
            },
        )
        self._checkpointer = InMemorySaver()
        self._agent_config = AgentConfig()
        self._tools = tools or []

    def create(self):
        return create_agent(
            model=self._model,
            tools=self._tools,
            system_prompt=self._agent_config.system_prompt,
            checkpointer=self._checkpointer,
        )
