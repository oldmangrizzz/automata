import abc
import logging
from enum import Enum
from typing import Any, Dict

import numpy as np
import openai

from automata_docs.core.database.vector import VectorDatabaseProvider
from automata_docs.core.symbol.symbol_types import Symbol

logger = logging.getLogger(__name__)


class NormType(Enum):
    L1 = "l1"
    L2 = "l2"
    SOFTMAX = "softmax"


class EmbeddingProvider(abc.ABC):
    """A class to provide embeddings for symbols"""

    @abc.abstractmethod
    def build_embedding(self, symbol_source: str) -> np.ndarray:
        pass


class OpenAIEmbedding(EmbeddingProvider):
    """A class to provide embeddings for symbols"""

    def __init__(self, engine: str = "text-embedding-ada-002"):
        if not openai.api_key:
            from config import OPENAI_API_KEY

            openai.api_key = OPENAI_API_KEY
        self.engine = engine

    def build_embedding(self, symbol_source: str) -> np.ndarray:
        """
        Get the embedding for a symbol.
        Args:
            symbol_source (str): The source code of the symbol
        Returns:
            A numpy array representing the embedding
        """
        # wait to import build_embedding to allow easy mocking of the function in tests.
        from openai.embeddings_utils import get_embedding

        return np.array(get_embedding(symbol_source, engine=self.engine))


class SymbolEmbeddingHandler(abc.ABC):
    """An abstract class to handle the embedding of symbols"""

    def __init__(
        self,
        embedding_db: VectorDatabaseProvider,
        embedding_provider: EmbeddingProvider,
    ):
        """An abstract constructor for SymbolEmbeddingHandler"""
        self.embedding_db = embedding_db
        self.embedding_provider = embedding_provider

    @abc.abstractmethod
    def get_embedding(self, symbol: Symbol) -> Any:
        """An abstract method to get the embedding for a symbol"""
        pass

    @abc.abstractmethod
    def update_embedding(self, symbol: Symbol):
        """An abstract method to update the embedding for a symbol"""
        pass


class EmbeddingSimilarity(abc.ABC):
    @abc.abstractmethod
    def get_query_similarity_dict(self, query_text: str) -> Dict[Any, float]:
        """An abstract method to get the similarity between a query and all symbols"""
        pass

    @abc.abstractmethod
    def get_nearest_entries_for_query(self, query_text: str, k_nearest: int) -> Dict[Any, float]:
        """An abstract method to get the k nearest symbols to a query"""
        pass
