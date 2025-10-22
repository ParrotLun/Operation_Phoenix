from langchain_openai import ChatOpenAI
from read_file_agent.utils.tools import tools
import os

# Initialize model with your custom config
model = ChatOpenAI(
    model="openai/gpt-oss-20b",
    temperature=0,
    base_url=os.getenv("OPENAI_API_BASE_URL", "http://172.16.120.65:8087/v1"),
    api_key=os.getenv("OPENAI_API_KEY") # type: ignore
)