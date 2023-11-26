import pydash
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from core.device.models import Device

User = get_user_model()


class DeviceTestCase(APITestCase):
    def test_registers_a_device(self):
        client = APIClient()
        response = client.post(
            reverse("device-register"), headers={"USER_AGENT": "useragent"}
        )
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(
            ["useragent"], pydash.pluck(Device.objects.all(), "user_agent")
        )

    def test_get_a_device_for_token(self):
        Device.objects.create(
            user_agent="useragent", token="939a9fd3-6b4c-4f64-bce0-c642d292df95"
        )
        self.assertEqual(
            "939a9fd3-6b4c-4f64-bce0-c642d292df95",
            str(Device.objects.for_token("939a9fd3-6b4c-4f64-bce0-c642d292df95").token),
        )
