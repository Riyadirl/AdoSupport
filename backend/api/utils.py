def success_response(message, data=None, status_code=200):
    return {
        "success": True,
        "statusCode": status_code,
        "message": message,
        "data": data
    }

def error_response(message, error_type="Error", status_code=400):
    return {
        "success": False,
        "statusCode": status_code,
        "errorType": error_type,
        "message": message
    }