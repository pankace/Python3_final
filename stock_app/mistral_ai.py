import logging
from django.conf import settings
from mistralai import Mistral

logger = logging.getLogger('stock_app')


class MistralAIClient:
    def __init__(self):
        self.api_key = settings.MISTRAL_API_KEY
        self.model_name = settings.MISTRAL_MODEL_NAME
        self.client = Mistral(api_key=self.api_key)  # Initialize the client as per Mistral AI's documentation

    def get_response(self, message: str, ticker: str, period: str, interval: str) -> str:
        """
        Get a response from Mistral AI based on the user's message, selected stock ticker, period, and interval.

        Args:
            message (str): The user's input message.
            ticker (str): The selected stock ticker symbol.
            period (str): The selected period (e.g., '1d', '5d', '1mo').
            interval (str): The selected interval (e.g., '1m', '5m', '1h').

        Returns:
            str: The AI's generated response.
        """
        try:
            # Construct the user message with comprehensive context
            user_content = (
                f"You are a financial advisor specializing in stock market strategies. "
                f"The user has selected the stock ticker '{ticker}' with a period of '{period}' and an interval of '{interval}'. "
                f"Based on the following message, provide a strategic analysis or advice: \"{message}\""
            )

            # Call the chat completion API
            chat_response = self.client.chat.complete(
                model=self.model_name,
                messages=[
                    {
                        "role": "user",
                        "content": user_content,
                    },
                ]
            )

            # Extract AI's response
            ai_text = chat_response.choices[0].message.content.strip()
            return ai_text

        except Exception as e:
            logger.error(f"Error communicating with Mistral AI: {e}")
            raise