def success_response(data=None, message: str = "success"):
    return {
        "code": 0,
        "message": message,
        "data": data,
    }


def error_response(message: str = "error", code: int = 1, data=None):
    return {
        "code": code,
        "message": message,
        "data": data,
    }
