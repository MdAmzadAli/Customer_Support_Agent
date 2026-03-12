from google.genai import Client
from mcp import ClientSession
from google.genai.types import GenerateContentConfig 
from typing import Optional
gemini_client:Optional[Client]=None
mcp_session:Optional[ClientSession]=None
config:Optional[GenerateContentConfig]=None