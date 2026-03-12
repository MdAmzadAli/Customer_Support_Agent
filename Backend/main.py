import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client
from contextlib import asynccontextmanager
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv, find_dotenv
from .utils import gb
from .Controller import query

load_dotenv(find_dotenv())

SYSTEM_INSTRUCTION = """
You are a receptionist at a hospital in Abu Dhabi.
Assist patients and visitors by answering their questions politely and professionally.
Keep all responses short, clear, and empathetic — people may be stressed or unwell.
Do not provide any medical advice or diagnosis. For medical concerns, always direct them to the relevant doctor or nurse.

You have access to tools to help you look up:
- Doctor availability
- Appointment booking
- Deleting booking
- Update booking
Use these tools whenever needed to give accurate, up-to-date information.
"""

@asynccontextmanager
async def lifespan(app: FastAPI):
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_GEMINI_API_KEY is not set in .env") 

    stdio_server = StdioServerParameters(
        command="python",
        args=["-m", "MCP_server.server"]
    )

    async with stdio_client(server=stdio_server) as (read, write):   
        async with ClientSession(read, write) as session:
            await session.initialize()

            server_tools = await session.list_tools()

            gemini_tools = types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.inputSchema
                    )
                    for tool in server_tools.tools
                ]
            )

            gb.gemini_client = genai.Client(api_key=api_key)         
            gb.config = types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=[gemini_tools]
            )
            gb.mcp_session = session                                   

            yield                                                      

          


app = FastAPI(
    title="Hospital Receptionist API",
    description="AI-powered hospital receptionist backed by Gemini + MCP tools",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query.router, prefix="/query", tags=["Query"])