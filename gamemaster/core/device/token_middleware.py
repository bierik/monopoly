class DeviceTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.device_token = request.headers.get("X-Device-Token", None)
        return self.get_response(request)
