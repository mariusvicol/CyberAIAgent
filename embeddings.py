from langchain_openai import OpenAIEmbeddings

def get_embeddings():
    return OpenAIEmbeddings(
    model="nomic-ai/nomic-embed-text-v2-moe-GGUF",
    base_url="https://lmstudio.ccrolabs.com/v1",
    api_key="asd",
    check_embedding_ctx_length=False,
    )   