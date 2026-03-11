import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from mcp import StdioServerParameters, ClientSession
from mcp.client.stdio import stdio_client
from contextlib import asynccontextmanager
from google import genai
from google.genai import types
import os
from dotenv import load_dotenv,find_dotenv
from pydantic import BaseModel

load_dotenv(find_dotenv())


gemini_client=None
gemini_tools=None
mcp_session=None
config=None
messages=[]

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
async def lifespan(app:FastAPI):
    global mcp_session, gemini_tools,gemini_client , config 
    stdio_server=StdioServerParameters(
        command="python",
        args=["-m", "MCP_server.server"]
    )
    
    stdio_object=stdio_client(server=stdio_server)
    read,write=await stdio_object.__aenter__()
    client_object=ClientSession(read,write)
    mcp_session=await client_object.__aenter__()
    await mcp_session.initialize()

    server_tools=await mcp_session.list_tools()
    
    gemini_tools=types.Tool(
        function_declarations=[types.FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=tool.inputSchema
        )
        for tool in server_tools.tools
        ]
    )
    api_key=os.getenv("GOOGLE_GEMINI_API_KEY")
    gemini_client=genai.Client(api_key=api_key)
    config=types.GenerateContentConfig(
    system_instruction=SYSTEM_INSTRUCTION,
    tools=[gemini_tools]
)

    yield

    await client_object.__aexit__(None,None,None)
    await stdio_object.__aexit__(None,None,None)


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

async def process_query(query:str): 
   
    messages.append(types.Content(role="user",parts=[types.Part(text=query)]))

    response=await gemini_client.aio.models.generate_content(
       model="gemini-2.5-flash-lite",
       config=config,
       contents=messages
    )

    parts=response.candidates[0].content.parts or []
    
    while any(part.function_call for part in parts):
        messages.append(response.candidates[0].content)
        function_responses=[]
        for part in parts:
            if part.function_call:
                result=await mcp_session.call_tool(
                    part.function_call.name, 
                    dict(part.function_call.args)
                    )
                raw=result.content[0].text
                parsed_result=json.loads(raw)
                function_responses.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                        id=part.function_call.id,
                        name=part.function_call.name,
                        response={"result":parsed_result}
                    )
                )
                )
        
        messages.append(types.Content(
            role="user",
            parts=function_responses+[types.Part(text="Please summarize the result for the user in a friendly way.")]
        ))
        
        response=await gemini_client.aio.models.generate_content(
       model="gemini-2.5-flash-lite",
       config=config,
       contents=messages
    )

        parts=response.candidates[0].content.parts or []

    if not parts or not any(part.text for part in parts):
        messages.append(types.Content(role="user",parts=[types.Part(text="Please summarize the result for the user in a friendly way.")]))
        response=await gemini_client.aio.models.generate_content(
       model="gemini-2.5-flash-lite",
       config=config,
       contents=messages
    )

        parts=response.candidates[0].content.parts
    
    if response.candidates and response.candidates[0].content:
        messages.append(response.candidates[0].content)
    
    text_parts=[part.text for part in parts]
    return "\n".join(text_parts) if text_parts else "I'm sorry, I couldn't generate a response."

class ChatRequest(BaseModel):
    query:str

class ChatResponse(BaseModel):
    response:str

@app.post("/query",response_model=ChatResponse)
async def query_path(request:ChatRequest):
    print("Query Received",request.query)
    try:
        query=request.query.strip()
        if not query :
            raise HTTPException(status_code=409,detail="Query is empty!") 
        if not mcp_session or not gemini_client:
            raise HTTPException(status_code=503, detail="Service not ready yet.")
    
        reply = await process_query(query)
        return ChatResponse(response=reply)
    except Exception as e:
        import traceback
        traceback.print_exc()  # prints full error in terminal
        raise HTTPException(status_code=500, detail=str(e))