import logging
from contextlib import contextmanager

from django.contrib.auth import get_user_model
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test.testcases import LiveServerThread, QuietWSGIRequestHandler
from playwright.sync_api import expect, sync_playwright

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
    board_base_url = "http://localhost:10000/board"
    player_base_url = "http://localhost:10000/player"

    def create_superuser(self):
        self.admin = User.objects.create(username="admin", is_superuser=True, is_staff=True)
        self.admin.set_password("admin")
        self.admin.save()

    def create_characters(self):
        self.zombie = create_character("Zombie", "zombie", order=0)
        self.chicken = create_character("Chicken", "chicken", order=1)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch()
        cls.expect = expect

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.close()
        cls.playwright.stop()

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
        ctx.set_default_timeout(1000)
        page = ctx.new_page()
        if as_user:
            page.request.post(
                "http://localhost:10000/api/login/",
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
        self.create_superuser()
        self.create_characters()
        self.board = monopoly_swiss.create()
