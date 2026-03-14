from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_core.documents.base import Document
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_qdrant import QdrantVectorStore
from loguru import logger


class LoadAndIndex:
    def __init__(
        self,
        file_path: str,
        embeddings: NVIDIAEmbeddings,
        url: str | None = None,
        collection_name: str = "novamark_services",
    ) -> None:
        self.file_path = file_path
        self.qdrant_url = url
        self.collection_name = collection_name
        self._documents: list[Document] = []
        self._embeddings = embeddings
        self._vector_store: QdrantVectorStore | None = None

    async def _get_or_create_vector_store(self) -> QdrantVectorStore:
        try:
            vector_store = QdrantVectorStore.from_existing_collection(
                embedding=self._embeddings,
                collection_name=self.collection_name,
                url=self.qdrant_url,
            )
            logger.info("Existing vector store collection found and loaded.")
            return vector_store
        except Exception as e:
            # check status code if it's a 404, then we know the collection doesn't exist and we can create it
            if hasattr(e, "status_code") and e.status_code == 404:
                logger.info(
                    "Vector store collection not found. Creating new collection..."
                )
            else:
                raise
            vector_store = await QdrantVectorStore.afrom_documents(
                documents=self._documents,
                embedding=self._embeddings,
                collection_name=self.collection_name,
                url=self.qdrant_url,
                prefer_grpc=True,
            )
            logger.info("New vector store collection created and indexed.")
            return vector_store

    async def _load_rag(self) -> list[Document]:
        loader = CSVLoader(file_path=self.file_path)
        documents = await loader.aload()
        logger.debug(f"Loaded {len(documents)} documents from {self.file_path}")
        return documents

    async def load_and_index(self):
        self._documents = await self._load_rag()
        self._vector_store = await self._get_or_create_vector_store()

    @property
    def vector_store(self) -> QdrantVectorStore | None:
        return self._vector_store
