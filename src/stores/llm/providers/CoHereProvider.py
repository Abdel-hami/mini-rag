from ..LLMInterface import LLMInterface
import logging
from ..LLMEnum import CohereRolesEnum, CohereInputType
import cohere

class CoHereProvider(LLMInterface):

    def __init__(self, api_key: str,
                    default_max_input_characters:int=1000,
                    default_generation_max_output_tokens:int=1000,
                    default_temperature:float=0.1):
        
        self.api_key = api_key
        self.default_max_input_characters = default_max_input_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_temperature = default_temperature

        self.client = cohere.ClientV2(
            api_key=api_key
            ) 

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None

        self.enums = CohereRolesEnum
        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size


    def generate_text(self, prompt: str, chat_history:list=[],max_output_tokens: int=None, temperature: float = None):

        if not self.client:
            self.logger.error("Client is not initialized")
            return None
        # if not self.embedding_model_id:
        #     self.logger.error("Embedding model is not set")
        #     return None

        max_output_tokens = self.default_generation_max_output_tokens if max_output_tokens is None else max_output_tokens
        temperature = self.default_temperature if temperature is None else temperature

        chat_history = self.construct_prompt(prompt, CohereRolesEnum.USER.value)


        response = self.client.chat(
            model=self.generation_model_id,
            messages=[chat_history],
            max_tokens=max_output_tokens,
            temperature=temperature,
            thinking= {
                "type":"disabled"
                },

        )
        for content in response.message.content:
            if content.type=="text":
                response_text = content.text

        print(response_text)
        if not response_text :
            self.logger.error("Generation failed")
            return None

        return response_text

    def embed_text(self, text: str, document_type: str=None):

        if not self.client:
            self.logger.error("Client is not initialized")
            return None
        if not self.embedding_model_id:
            self.logger.error("Embedding model is not set")
            return None
        ###
        input_type = CohereInputType.SEARCH_DOCUMENT.value
        if document_type == CohereInputType.SEARCH_QUERY.value:
            input_type = CohereInputType.SEARCH_QUERY.value

        response = self.client.embed(
            texts=[self.process_text(text)],
            model=self.embedding_model_id,
            input_type=input_type,
            embedding_types=["float"],
        
            # output_dimension=384,
        )
        
        if not response or not response.embeddings or not response.embeddings.float[0] :
            self.logger.error("Embedding failed")
            return None
        
        return response.embeddings.float[0]

    def process_text(self, text: str):
        return text[:self.default_max_input_characters].strip()

    def construct_prompt(self, prompt: str, role: str):
        return {
            "role": role,
            "content": prompt
            # "content": self.process_text(prompt)
        }




