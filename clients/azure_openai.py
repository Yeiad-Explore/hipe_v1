"""Azure OpenAI client wrapper."""
import os
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class AzureOpenAIClient:
    """Wrapper for Azure OpenAI API with retry logic."""

    def __init__(self):
        """Initialize Azure OpenAI client."""
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.chat_deployment = os.getenv("CHAT_MODEL_DEPLOYMENT")
        self.embedding_deployment = os.getenv("EMBEDDING_MODEL_DEPLOYMENT")

        if not all([self.api_key, self.endpoint, self.api_version]):
            raise ValueError("Missing Azure OpenAI configuration in .env")

        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint,
        )
        logger.info("Azure OpenAI client initialized")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        response_format: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Get chat completion from Azure OpenAI.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            response_format: Optional response format (e.g., {"type": "json_object"})

        Returns:
            str: Generated response
        """
        try:
            kwargs = {
                "model": self.chat_deployment,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = self.client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            logger.debug(f"Chat completion successful. Tokens used: {response.usage.total_tokens}")
            return content

        except Exception as e:
            logger.error(f"Chat completion error: {e}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List[List[float]]: List of embedding vectors
        """
        try:
            # Azure OpenAI embeddings API can handle multiple texts at once
            response = self.client.embeddings.create(
                model=self.embedding_deployment,
                input=texts,
            )
            embeddings = [item.embedding for item in response.data]
            logger.debug(f"Generated embeddings for {len(texts)} texts")
            return embeddings

        except Exception as e:
            logger.error(f"Embedding generation error: {e}")
            raise

    def get_single_embedding(self, text: str) -> List[float]:
        """
        Get embedding for a single text.

        Args:
            text: Text string to embed

        Returns:
            List[float]: Embedding vector
        """
        embeddings = self.get_embeddings([text])
        return embeddings[0]

    def structured_output(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
        temperature: float = 0.3,
    ) -> str:
        """
        Get structured JSON output.

        Args:
            messages: List of message dicts
            system_prompt: System prompt with JSON schema instructions
            temperature: Lower temperature for more consistent JSON

        Returns:
            str: JSON string response
        """
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        return self.chat_completion(
            messages=full_messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
