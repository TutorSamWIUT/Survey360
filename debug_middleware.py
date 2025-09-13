import logging

logger = logging.getLogger(__name__)

class DebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.debug(f"REQUEST: {request.method} {request.get_full_path()}")
        logger.debug(f"HEADERS: {dict(request.headers)}")
        logger.debug(f"META: {request.META}")
        
        response = self.get_response(request)
        
        logger.debug(f"RESPONSE: {response.status_code}")
        logger.debug(f"RESPONSE HEADERS: {dict(response.headers) if hasattr(response, 'headers') else 'No headers'}")
        
        return response