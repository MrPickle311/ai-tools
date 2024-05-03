import redis
from langchain_community.document_loaders import pdf
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStore
from langchain_openai import OpenAIEmbeddings


def is_embedding_in_keys(hashmap_name: str, filename: str, redis_client: redis.Redis) -> bool:
    if hashmap_name.encode() not in redis_client.keys("*"):
        return False

    result = filename.encode() in redis_client.hkeys(hashmap_name)

    if result:
        print(f'Found embedding {filename} in {hashmap_name} embedding store')
    return result


def get_embeddings(hashmap_name: str, filename: str, redis_client: redis.Redis) -> bytes:
    return redis_client.hget(hashmap_name, filename)


def save_embeddings(hashmap_name: str, filename: str, redis_client: redis.Redis, data: bytes) -> None:
    redis_client.hset(hashmap_name, filename, data)


def get_pages_from_pdf(filename: str, start_page: int, end_page: int) -> list[Document]:
    loader = pdf.PyPDFLoader(
        file_path=filename
    )
    return loader.load_and_split()[start_page:end_page]


def make_vectors(filename: str, start_page: int, end_page: int, redis_client: redis.Redis,
                 hashmap_name: str) -> VectorStore:
    final_filename = f'{filename}_{start_page}_{end_page}'
    if is_embedding_in_keys(hashmap_name, final_filename, redis_client):
        return FAISS.deserialize_from_bytes(
            serialized=get_embeddings(hashmap_name, filename, redis_client),
            embeddings=OpenAIEmbeddings()
        )
    embeddings = OpenAIEmbeddings()

    pages = get_pages_from_pdf(filename, start_page, end_page)

    result = FAISS.from_documents(pages, embeddings)

    to_save = result.serialize_to_bytes()
    save_embeddings(hashmap_name, final_filename, redis_client, to_save)

    return result


def save_md_file(filename: str, content: str) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
