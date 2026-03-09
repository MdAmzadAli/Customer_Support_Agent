def response_schema(success: bool, message: str, data: dict = None) -> dict:
    return {
        "success": success,
        "message": message,
        "data":    data if data is not None else {}
    }