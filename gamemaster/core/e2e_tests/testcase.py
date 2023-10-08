import logging
import shlex
import subprocess
from contextlib import contextmanager

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.testcases import LiveServerThread, QuietWSGIRequestHandler
from playwright.sync_api import expect, sync_playwright
from requests.adapters import HTTPAdapter
from rest_framework import status
from urllib3.util.retry import Retry

from core.board import monopoly_swiss
from core.game.tests import create_character
from core.testutils import create_player

User = get_user_model()


logger = logging.getLogger("e2e-testing")


class LiveServerThreadWithReuse(LiveServerThread):
    """
    Allows port reuse and avoids creating "address already in use" errors
    """

    def _create_server(self, **kwargs):
        return self.server_class(
            (self.host, self.port),
            QuietWSGIRequestHandler,
            allow_reuse_address=True,
            **kwargs,
        )


class E2ETestCase(StaticLiveServerTestCase):
    server_thread_class = LiveServerThreadWithReuse
    port = 50000
    board_base_url = "http://localhost:5000/board"
    player_base_url = "http://localhost:5000/player"

    @classmethod
    def create_superuser(cls):
        admin = User.objects.create(username="admin", is_superuser=True, is_staff=True)
        admin.set_password("admin")
        admin.save()

    @classmethod
    def create_characters(cls):
        cls.zombie = create_character("Zombie", "zombie", order=0)
        cls.chicken = create_character("Chicken", "chicken", order=1)

    @classmethod
    def wait_for_endpoint(cls, url):
        status_forcelist = [
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            status.HTTP_502_BAD_GATEWAY,
            status.HTTP_503_SERVICE_UNAVAILABLE,
            status.HTTP_504_GATEWAY_TIMEOUT,
        ]
        retry_strategy = Retry(total=5, status_forcelist=status_forcelist, backoff_factor=0.05, raise_on_status=False)
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount("http://", adapter)
        try:
            response = session.get(url)
        except requests.exceptions.RequestException:
            logger.exception("Endpoint was not ready")
            return False
        else:
            return response.status_code == status.HTTP_200_OK

    @classmethod
    def start_frontend(cls):
        subprocess.run(  # noqa: S603
            shlex.split("docker compose -f compose.yaml up -d --build"),
            cwd=settings.BASE_DIR.parent,
            check=True,
            shell=False,
            capture_output=True,
            text=True,
        )
        cls.wait_for_endpoint(cls.board_base_url)
        cls.wait_for_endpoint(cls.player_base_url)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_superuser()
        cls.create_characters()
        cls.board = monopoly_swiss.create()
        print(f"Live server listening on {cls.live_server_url}")  # noqa: T201
        cls.start_frontend()
        cls.p = sync_playwright().start()
        cls.browser = cls.p.chromium.launch(headless=False)
        cls.expect = expect

    @classmethod
    def login(cls, username, password):
        cls.context.request.post("/api/login", data={"username": username, "password": password})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()
        cls.p.stop()

    @classmethod
    def wait_for_nuxt(cls, page):
        nuxt_root = page.locator("#__nuxt")
        nuxt_root.wait_for(state="attached", timeout=120_000)

    @contextmanager
    def board_page(self, path="/"):
        ctx = self.browser.new_context(user_agent="e2e-testing")
        page = ctx.new_page()
        page.goto(f"{self.board_base_url}{path}")
        self.wait_for_nuxt(page)
        try:
            yield page
        finally:
            page.close()
            ctx.close()

    @contextmanager
    def player_page(self, path="/", as_user="player"):
        ctx = self.browser.new_context(user_agent="e2e-testing", viewport={"width": 375, "height": 668})
        page = ctx.new_page()
        if as_user:
            page.request.post(
                f"{self.player_base_url}/api/login/",
                data={"username": as_user, "password": "player"},
            )
        page.goto(f"{self.player_base_url}{path}")
        self.wait_for_nuxt(page)
        try:
            yield page
        finally:
            page.close()
            ctx.close()

    def setUp(self):
        self.player = create_player("player", "player")
