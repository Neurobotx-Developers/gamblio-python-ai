from sentence_transformers import SentenceTransformer
EMBEDDING_MODEL = SentenceTransformer(
    "sentence-transformers/distiluse-base-multilingual-cased-v2"
)


def calculate_embedding(text: str) -> str:
    embedding = EMBEDDING_MODEL.encode(text)

    embedding_str = "["
    i = 0
    for dimension in embedding:
        embedding_str += "{}".format(dimension)
        if i < len(embedding) - 1:
            embedding_str += ", "
        i += 1
    embedding_str += "]"

    return embedding_str
