from langchain_core.tools import tool
from langchain_core.tools.base import BaseTool
from langchain_qdrant import QdrantVectorStore


class RetrieverTool:
    def __init__(self, vector_store: QdrantVectorStore, k: int = 2):
        self.vector_store = vector_store
        self.k = k
        self._retriever_tool = self._build_tool()

    def _build_tool(self) -> BaseTool:
        @tool("retriever_tool")
        async def retriever_tool(query: str) -> str:
            """Search the NovaMark Digital knowledge base for information about services, pricing, processes, and FAQs."""
            results = await self.vector_store.asimilarity_search(query, k=self.k)
            return "\n".join([result.page_content for result in results])

        return retriever_tool

    @property
    def retriever_tool(self) -> BaseTool:
        return self._retriever_tool
