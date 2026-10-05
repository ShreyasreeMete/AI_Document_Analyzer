import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

GROQ_MODEL = "openai/gpt-oss-20b"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

CHUNK_SIZE = 1000        # characters per chunk
CHUNK_OVERLAP = 200      # characters shared between neighbouring chunks
TOP_K = 5                # chunks retrieved for each question
MAX_CONTEXT_CHARS = 18000  # cap on text sent to the LLM (keeps within Groq free-tier limits)

SUPPORTED_TYPES = ["pdf", "docx", "txt", "csv"]
