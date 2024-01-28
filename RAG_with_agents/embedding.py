__created__ = "28.01.2024"
__last_update__ = "28.01.2024"
__author__ = "https://github.com/pyautoml"
__version__ = "1.0.0"


import gc
import os
import sys
import torch.cuda
from tools import Tools
from typing import List
from logger import logger
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PDFMinerLoader,
    DirectoryLoader,
    UnstructuredPDFLoader,
)


class AbstractEmbedding(ABC):
    def create_embedding(self, text: str) -> list:
        pass

class HuggingFaceEmbedding(AbstractEmbedding):
    def __init__(
        self,
        credentials: dict,
        embedding_model: str,
        chunk_size: int,
        chunk_overlap: int,
        cache_folder: str = "local_cache",
    ) -> None:
        self.credentials = credentials
        os.environ["HUGGINGFACEHUB_API_TOKEN"] = self.credentials["api_key"]

        # set device
        self.device = "gpu" if torch.cuda.is_available() else "cpu"

        # local cache
        self.cache_folder = cache_folder
        Tools.create_directory(cache_folder)

        # model name and dimension
        self.model_name = embedding_model["name"]
        self.model_dim_size = embedding_model["dim_size"]
        self.supported_models = [
            self.credentials["model"][model]["name"]
            for model in self.credentials["model"]
        ]
        if self.model_name in self.supported_models:
            self.model = Tools.load_model(
                model_name=self.model_name, cache_folder=self.cache_folder
            )
        else:
            logger.critical(
                f"Model not supported. Currently supported models: {self.supported_models}"
            )
            sys.exit(1)

        self.recursive_text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
        )

        del self.credentials
        gc.collect()

    def create_embedding(self, text: [str | list]) -> [str | list]:
        if isinstance(text, list):
            return self.create_multiple_embeddings(text)
        else:
            return self.create_single_embedding(text)

    def create_single_embedding(self, sentence: str) -> str:
        return self.model.encode(sentence)

    def create_multiple_embeddings(self, sentences: List[str]) -> None:
        return list(map(self.create_single_embedding, sentences))

    def process_single_pdf(self, path_to_pdf: str) -> None:
        loader = PDFMinerLoader(path_to_pdf)
        data = loader.load()
        return self._recursive_text_splitter.split_documents(data)

    def process_texts(self, text: str) -> None:
        return self._recursive_text_splitter.split_text(text)
