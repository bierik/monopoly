from core.device.models import Device


class DeviceTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        device_token = request.headers.get("X-Device-Token", None)
        try:
            request.device = Device.objects.for_token(device_token) if device_token else None
        except Device.DoesNotExist:
            request.device = None
        return self.get_response(request)
