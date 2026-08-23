from enum import Enum

class LLMEnum(Enum):
    OPENAI = "openai"
    COHERE = "cohere"


class OpenAIRolesEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class CohereRolesEnum(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "chatbot"

class CohereInputType(Enum):
    SEARCH_QUERY = "search_query"
    SEARCH_DOCUMENT = "search_document"