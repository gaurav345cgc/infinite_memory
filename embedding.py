import os
from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
from logging_config import setup_logging
from typing import List, Optional, Dict

# Initialize logger for this module
logger = setup_logging(__name__)

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("Missing OPENAI_API_KEY environment variable")
    raise ValueError("Missing OPENAI_API_KEY environment variable")

# Use the new OpenAI v1 client
client = OpenAI(api_key=OPENAI_API_KEY)
logger.info("OpenAI client initialized for embeddings")


def generate_embedding(text: str, metadata: Optional[Dict[str, str]] = None) -> List[float]:
    """
    Generate an embedding vector for a given text.
    Metadata is accepted for downstream compatibility but not used here.
    """
    try:
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input=text
        )
        embedding_vector = response.data[0].embedding
        logger.debug(f"Generated embedding vector of length {len(embedding_vector)}")
        return embedding_vector
    except OpenAIError as e:
        logger.error(f"OpenAI API error: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise
