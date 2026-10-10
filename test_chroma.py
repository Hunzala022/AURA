import sys

import chromadb
from chromadb.utils import embedding_functions

def test_chroma():
    default_ef = embedding_functions.DefaultEmbeddingFunction()
    emb = default_ef(["test document"])
    print("Embedding length:", len(emb[0]))

if __name__ == "__main__":
    test_chroma()
