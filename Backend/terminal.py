from  google import genai
from google.genai import types

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

async def run_terminal():
    server_pararms=StdioServerParameters(
        command="python",
        args=["-m","MCP_server.server"]
    )

    async with stdio_client(server=server_pararms) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()

            tools=await session.list_tools()

            gemini_tools=types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=tool.name,
                        description=tool.description,
                        parameters=tool.inputSchema
                    )
                    for tool in tools.tools
                ]
            )

            print("✅ Connected to MCP Server")
            print(f"✅ Tools available: {[t.name for t in tools.tools]}")
            print("-" * 50)
            print("Type your message below. Type 'exit' to quit.")
            print("-" * 50)
            
            messages=[]
            api_key=os.getenv("GOOGLE_GEMINI_API_KEY")
            client=genai.Client(api_key=api_key)
            system_instruction = """
You are a receptionist at a hospital in Abu Dhabi.
Assist patients and visitors by answering their questions politely and professionally.
Keep all responses short, clear, and empathetic — people may be stressed or unwell.
Do not provide any medical advice or diagnosis. For medical concerns, always direct them to the relevant doctor or nurse.

You have access to tools to help you look up:
- Doctor availability
- Appointment booking 
- Deleting booking
- update booking
Use these tools whenever needed to give accurate, up-to-date information.
"""
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[gemini_tools]
            )

            while True:

                user_input=input("\nYou:").strip()
                if not user_input:
                    print("please provide some text")
                    continue
                if user_input=="exit":
                    break

                
                messages.append(
                    types.Content(role="user",parts=[types.Part(text=user_input)])
                )

                response=await client.aio.models.generate_content(
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
                            tool_result=await session.call_tool(
                                part.function_call.name,
                                dict(part.function_call.args)
                                )
                            raw=tool_result.content[0].text 
                            parsed_result=json.loads(raw)
                            print("\nDEBUG: ",parsed_result,"\nRaw :", raw, "\nTool Result:",tool_result)
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
                    # await asyncio.sleep()
                    response=await client.aio.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    config=config,
                    contents=messages
                    )
                    # print("\nRESONPONSE: ",response)
                    parts=response.candidates[0].content.parts or []
                
                if not parts or not any(part.text for part in parts):
                    print("\nNo Parts in Gemini Response")
                    messages.append(types.Content(role="user",parts=[types.Part(text="Please summarize the result for the user in a friendly way.")]))
                    response=await client.aio.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    config=config,
                    contents=messages
                    )
                    parts=response.candidates[0].content.parts
                
                if response.candidates and response.candidates[0].content:
                    messages.append(response.candidates[0].content)
                for part in parts:
                    if part.text:
                        print(f"\nAssistant: {part.text}")



























if __name__=="__main__":
    asyncio.run(run_terminal())