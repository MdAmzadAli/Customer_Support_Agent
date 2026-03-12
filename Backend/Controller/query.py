from fastapi import APIRouter, Depends, HTTPException  
from pydantic import BaseModel
from google.genai import types
from ..utils import gb
import json
from ..utils.try_catch_wrapper import catch_errors
from ..utils.jwt_auth import verify_access_token

router = APIRouter()

conversation_history = {}
MAX_HISTORY = 20


async def process_query(query: str, messages: list):
    messages.append(types.Content(role="user", parts=[types.Part(text=query)]))

    response = await gb.gemini_client.aio.models.generate_content(
        model="gemini-2.5-flash-lite",
        config=gb.config,
        contents=messages
    )

    parts = response.candidates[0].content.parts or []

    while any(part.function_call for part in parts):
        messages.append(response.candidates[0].content)
        function_responses = []

        for part in parts:
            if part.function_call:
                result = await gb.mcp_session.call_tool(
                    part.function_call.name,
                    dict(part.function_call.args)
                )
                raw = result.content[0].text
                parsed_result = json.loads(raw)
                function_responses.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            id=part.function_call.id,
                            name=part.function_call.name,
                            response={"result": parsed_result}
                        )
                    )
                )

        messages.append(types.Content(
            role="user",
            parts=function_responses + [types.Part(text="Please summarize the result for the user in a friendly way.")]
        ))

        response = await gb.gemini_client.aio.models.generate_content(
            model="gemini-2.5-flash-lite",
            config=gb.config,
            contents=messages
        )
        parts = response.candidates[0].content.parts or []

    if not parts or not any(part.text for part in parts):
        messages.append(types.Content(
            role="user",
            parts=[types.Part(text="Please summarize the result for the user in a friendly way.")]
        ))
        response = await gb.gemini_client.aio.models.generate_content(
            model="gemini-2.5-flash-lite",
            config=gb.config,
            contents=messages
        )
        parts = response.candidates[0].content.parts

    if response.candidates and response.candidates[0].content:
        messages.append(response.candidates[0].content)

    text_parts = [part.text for part in parts if part.text]
    return "\n".join(text_parts) if text_parts else "I'm sorry, I couldn't generate a response."


class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str


@router.post("/")
@catch_errors
async def query_path(request: ChatRequest, user_id: str = Depends(verify_access_token)): 
    query = request.query.strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query is empty!")

    if not gb.mcp_session or not gb.gemini_client:
        raise HTTPException(status_code=503, detail="Service not ready yet.")

    messages = conversation_history.get(user_id, [])
    reply = await process_query(query, messages)
    conversation_history[user_id] = messages[-MAX_HISTORY:]  
    return ChatResponse(response=reply)