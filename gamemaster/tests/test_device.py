import pydash
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from app.device.models import Device


User = get_user_model()


class DeviceTestCase(APITestCase):
    def test_registers_a_device(self):
        client = APIClient()
        response = client.post(reverse("device-register"), headers={"USER_AGENT": "useragent"})
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual("useragent", response.json()["user_agent"])
        self.assertEqual(["useragent"], pydash.pluck(Device.objects.all(), "user_agent"))

    def test_does_not_register_a_device_twice(self):
        Device.objects.create(user_agent="useragent", token="939a9fd3-6b4c-4f64-bce0-c642d292df95")  # noqa: S106
        client = APIClient()
        response = client.post(
            reverse("device-register"),
            headers={"X-Device-Token": "939a9fd3-6b4c-4f64-bce0-c642d292df95"},
        )
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual("939a9fd3-6b4c-4f64-bce0-c642d292df95", response.json()["token"])
        self.assertEqual(
            ["939a9fd3-6b4c-4f64-bce0-c642d292df95"],
            list(map(str, Device.objects.values_list("token", flat=True))),
        )
