# groq_llm.py

import os  # Used to access environment variables
from pydantic import PrivateAttr  # Used to store non-serializable objects (like API clients)
from langchain_core.language_models.llms import LLM  # creating own custom LLM (updated import)
from groq import Groq  # connect to Groq API


class GroqLLM(LLM):  # Inherits from LangChain’s LLM base class

    _groq_client: Groq = PrivateAttr()  # 🔥 Private attribute so Pydantic does NOT try to serialize it
    temperature: float = 0.7  # Controls randomness of output

    def __init__(self, **data):
        """
        Initialize the Groq client manually instead of using root_validator
        """
        super().__init__(**data)  # Initialize parent LLM class

        api_key = os.getenv("GROQ_API_KEY")  # Reads API key from environment variable

        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self._groq_client = Groq(api_key=api_key)  # Creates Groq client instance

    @property
    def _llm_type(self) -> str:  # Identifies the type of LLM
        return "groq"

    def _call(self, prompt: str, **kwargs) -> str:
        """
        Main method that:
        - Sends prompt to Groq
        - Returns response
        """

        response = self._groq_client.chat.completions.create(  # Calls Groq’s chat completion API
            messages=[{"role": "user", "content": prompt}],  # Formats input as chat message

            # you can parameterize model name if you want:
            model=kwargs.pop("model", "llama-3.3-70b-versatile"),

            temperature=self.temperature,
            **kwargs  # Passes any additional parameters
        )

        return response.choices[0].message.content  # Extract and return generated text


# Loads API key
# Creates Groq client automatically
# Sends prompt to Groq model
# Returns generated text
# Works inside LangChain