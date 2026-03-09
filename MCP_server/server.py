import asyncio
import json
from datetime import datetime
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types
from .Tools import check_availability,book_appointment,update_appointment,delete_appointment
from Database.db_init import sessionLocal
import logging
import os

server=Server("Customer-Support")

@server.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="check_availability",
            description="Check availability of a particular date for booking an appointment",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format (e.g. '2025-12-23')"
                    }
                },
                "required": ["date"]
            }
        ),
        types.Tool(
            name="book_appointment",
            description="Book a new appointment for a given date",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the person booking the appointment"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format (e.g. '2025-12-23')"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the appointment"
                    }
                },
                "required": ["name", "date", "reason"]
            }
        ),
        types.Tool(
            name="update_appointment",
            description="Update an existing appointment by name and date",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the person whose appointment to update"
                    },
                    "date": {
                        "type": "string",
                        "description": "Current date of the appointment in YYYY-MM-DD format"
                    },
                    "newName": {
                        "type": "string",
                        "description": "New name to update to (optional)"
                    },
                    "newDate": {
                        "type": "string",
                        "description": "New date in YYYY-MM-DD format (optional)"
                    },
                    "newReason": {
                        "type": "string",
                        "description": "New reason to update to (optional)"
                    }
                },
                "required": ["name", "date"]
            }
        ),
        types.Tool(
            name="delete_appointment",
            description="Delete an existing appointment by name and date",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Full name of the person whose appointment to delete"
                    },
                    "date": {
                        "type": "string",
                        "description": "Date of the appointment to delete in YYYY-MM-DD format"
                    }
                },
                "required": ["name", "date"]
            }
        ),
    ]

log_path=os.path.join(os.path.dirname(__file__),"debug.log")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path,"w"),  # ← writes here
    ]
)
logger = logging.getLogger(__name__)


@server.call_tool()
async def router(name: str, arguments: dict) -> list[types.TextContent]:
    logger.info(f"Tool called: '{name}'")
    logger.debug(f"Arguments received: {arguments}")

    async with sessionLocal() as session:
        async with session.begin():
            try:
                if name == "check_availability":
                    logger.debug(f"check_availability → date={arguments.get('date')}")
                    result = await check_availability(
                        session,
                        arguments["date"]
                    )

                elif name == "book_appointment":
                    logger.debug(f"book_appointment → name={arguments.get('name')}, date={arguments.get('date')}, reason={arguments.get('reason')}")
                    result = await book_appointment(
                        session,
                        arguments["name"],
                        arguments["date"],
                        arguments["reason"]
                    )

                elif name == "update_appointment":
                    logger.debug(f"update_appointment → name={arguments.get('name')}, date={arguments.get('date')}, newName={arguments.get('newName')}, newDate={arguments.get('newDate')}, newReason={arguments.get('newReason')}")
                    result = await update_appointment(
                        session,
                        arguments["name"],
                        arguments["date"],
                        arguments.get("newName", ""),
                        arguments.get("newDate", ""),
                        arguments.get("newReason", "")
                    )

                elif name == "delete_appointment":
                    logger.debug(f"delete_appointment → name={arguments.get('name')}, date={arguments.get('date')}")
                    result = await delete_appointment(
                        session,
                        arguments["name"],
                        arguments["date"]
                    )

                else:
                    logger.warning(f"Unknown tool called: '{name}'")
                    result = {"success": False, "message": f"Unknown tool: '{name}'"}

            except KeyError as e:
                logger.error(f"Missing argument for '{name}': {e}")
                logger.debug(f"Arguments that were provided: {arguments}")
                result = {"success": False, "message": f"Missing required argument: {e}"}

            except ValueError as e:
                logger.error(f"ValueError in '{name}': {e}")
                result = {"success": False, "message": str(e)}

            except Exception as e:
                logger.exception(f"Unexpected error in '{name}': {e}")
                result = {"success": False, "message": f"Unexpected error: {str(e)}"}

    logger.info(f"Tool '{name}' result → success={result.get('success')}, message={result.get('message')}")
    return [types.TextContent(type="text", text=json.dumps(result))]


async def main():
    async with stdio_server() as (readstream, writestream):
        await server.run(
            readstream,
            writestream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
                   

          


    