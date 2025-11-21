from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.models.openai import OpenAIModel

from ...config import settings

# Initialize OpenAI model for agent interactions
openai_model = OpenAIModel(
    model_name="gpt-4-turbo-preview",
    provider=OpenAIProvider(api_key=settings.openai_api_key),
    system_prompt_role="system",
)
