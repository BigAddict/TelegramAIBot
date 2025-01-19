from pydantic import BaseModel
from dotenv import load_dotenv
from google.genai import types
from google import genai
import logging
import json
import os

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Loading enviroment variables
load_dotenv("../")

class Agent:
    GEMINI_KEY = os.getenv("GEMINI_API")

    class ContentParameters(BaseModel):
        system_information: str
        prompt: str
        thumbnail_prompt: str
        temparature: float
        top_p: float
        top_k: int
        debugger_message: str

    class ContentSchema(BaseModel):
        content_md: str
        explanatory_lines : str
        debugger_message: str

    def __init__(self):
        self.client = genai.Client(api_key=self.GEMINI_KEY)

    def moderator(self)->dict:
        prompt = "You are an AI agent tasked with crafting a single, concise prompt for a Telegram content generation AI agent. This prompt should be designed to elicit creative and engaging blog like content suitable for a Telegram channel focused on technology and finance."
        response = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.45,
                top_p=0.95, top_k=40,
                response_mime_type="application/json",
                response_schema=self.ContentParameters
            )
        )
        formatted_response = json.loads(response.text)
        logger.info(formatted_response["debugger_message"])
        return formatted_response

    def generate_content(self) -> dict:
        parameters = self.moderator()
        generated_content = self.client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=parameters["prompt"],
            config=types.GenerateContentConfig(
                system_instruction=parameters["system_information"],
                temperature=parameters["temparature"],
                top_p=parameters["top_p"],
                top_k=parameters["top_k"],
                response_mime_type="application/json",
                response_schema=self.ContentSchema
            )
        )
        formatted_response = json.loads(generated_content.text)
        logger.info(formatted_response["debugger_message"])
        return formatted_response
    
if __name__ == "__main__":
    agent = Agent()
    response = agent.generate_content()
    print(response)