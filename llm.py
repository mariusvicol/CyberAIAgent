from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="deepseek/deepseek-r1-0528-qwen3-8b",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key="asd",
    base_url="https://lmstudio.ccrolabs.com/v1",
)