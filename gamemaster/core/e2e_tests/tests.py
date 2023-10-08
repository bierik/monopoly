import random
import re

from core.device.models import Device
from core.e2e_tests.testcase import E2ETestCase
from core.game.models import Game
from core.testutils import create_player, inject_device_token


class GameRegistrationTestCase(E2ETestCase):
    def test_registers_a_device(self):
        with self.board_page() as page:
            self.expect(page.get_by_text("Registrieren", exact=True)).to_be_visible()
            self.assertEqual(["e2e-testing"], list(Device.objects.values_list("user_agent", flat=True)))

    def test_logs_in_the_player(self):
        device = Device.objects.create()
        with self.player_page(f"/game/create/{device.token}", as_user=None) as page:
            page.get_by_placeholder("Benutzername").type("player")
            page.get_by_placeholder("Passwort").type("player")
            page.get_by_test_id("login-button").click()
            self.expect(page.get_by_text("Neues Spiel erstellen", exact=True)).to_be_visible()

    def test_creates_a_new_game(self):
        with self.board_page() as board_page:
            self.expect(board_page.get_by_text("Registrieren", exact=True)).to_be_visible()
            device = Device.objects.first()

            with self.player_page(f"/game/create/{device.token}") as page:
                page.get_by_label("Anzahl Spieler").type("2")
                page.get_by_label("Spielbrett").select_option("monopoly")
                page.get_by_test_id("create-new-game-button").click()
                self.expect(page.get_by_test_id("character-name")).to_have_text(["Zombie", "Chicken"])
                self.assertEqual([self.player.pk], list(Game.objects.values_list("owner__id", flat=True)))

                self.expect(board_page.get_by_text("Spiel beitreten", exact=True)).to_be_visible()

    def test_players_join_the_lobby(self):
        device = Device.objects.create()
        game = Game.objects.create(owner=self.player, board=self.board, device=device)

        with self.board_page() as board_page:
            inject_device_token(board_page, device)
            board_page.goto(f"{self.board_base_url}/lobby/{game.id}")
            self.expect(board_page.get_by_test_id("missing-participation")).to_have_count(4)

            with self.player_page(f"/game/{game.pk}/join") as player_page:
                player_page.get_by_text("Zombie", exact=True).click()
                player_page.get_by_test_id("select-character-button").click()

                self.expect(board_page.get_by_test_id("missing-participation")).to_have_count(3)
                self.expect(board_page.get_by_test_id("participation-username")).to_have_text(["player"])

    def test_owner_can_start_the_game_as_soon_as_the_lobby_is_full(self):
        device = Device.objects.create()
        game = Game.objects.create(owner=self.player, board=self.board, device=device, max_participations=2)
        create_player(username="other.player")

        with self.player_page(f"/game/{game.pk}/join") as player_page:
            player_page.get_by_text("Zombie", exact=True).click()
            player_page.get_by_test_id("select-character-button").click()
            self.expect(player_page.get_by_test_id("start-game-button")).to_be_disabled()

            with self.player_page(f"/game/{game.pk}/join", as_user="other.player") as other_player_page:
                other_player_page.get_by_text("Chicken", exact=True).click()
                other_player_page.get_by_test_id("select-character-button").click()
                self.expect(other_player_page.get_by_text("Warten auf Spielstart")).to_be_visible()

                self.expect(player_page.get_by_test_id("start-game-button")).not_to_be_disabled()
                player_page.get_by_test_id("start-game-button").click()
                self.expect(player_page.get_by_text("Würfeln", exact=True)).to_be_visible()
                self.expect(other_player_page.get_by_text("Würfeln", exact=True)).to_be_visible()

    def test_board_show_game_when_game_has_started(self):
        device = Device.objects.create()
        game = Game.objects.create(owner=self.player, board=self.board, device=device, max_participations=1)

        with self.board_page() as board_page:
            inject_device_token(board_page, device)
            board_page.goto(f"{self.board_base_url}/lobby/{game.id}")

            with self.player_page(f"/game/{game.pk}/join") as player_page:
                player_page.get_by_text("Zombie", exact=True).click()
                player_page.get_by_test_id("select-character-button").click()
                player_page.get_by_test_id("start-game-button").click()

            self.expect(board_page).to_have_url(re.compile(rf"game/{game.pk}"))

    def test_player_can_roll_dice_and_character_moves(self):
        random.seed(42)
        device = Device.objects.create()
        game = Game.objects.create(owner=self.player, board=self.board, device=device, max_participations=1)
        participation = game.join(self.player, self.zombie)
        self.assertEqual("start", participation.current_tile.identifier)

        with self.player_page(f"/game/{game.pk}/play") as player_page:
            self.expect(player_page.get_by_test_id("roll-dice-button")).to_be_disabled()
            game.start()
            self.expect(player_page.get_by_test_id("roll-dice-button")).to_be_enabled()
            with player_page.expect_response(lambda response: "move" in response.url):
                player_page.get_by_test_id("roll-dice-button").click()
            participation.refresh_from_db()
            self.assertEqual("chance3", participation.current_tile.identifier)

    def test_player_can_end_turn_after_dice_are_rolled(self):
        device = Device.objects.create()
        game = Game.objects.create(owner=self.player, board=self.board, device=device, max_participations=1)
        participation = game.join(self.player, self.zombie)

        with self.player_page(f"/game/{game.pk}/play") as player_page:
            self.expect(player_page.get_by_test_id("end-turn-button")).to_be_disabled()
            game.start()
            participation.move(1)
            self.expect(player_page.get_by_test_id("end-turn-button")).to_be_enabled()
            self.expect(player_page.get_by_test_id("roll-dice-button")).to_be_disabled()

    def test_other_player_can_roll_dice_when_previous_player_has_ended_its_turn(self):
        other_player = create_player(username="other.player")
        device = Device.objects.create()
        game = Game.objects.create(owner=self.player, board=self.board, device=device, max_participations=2)
        participation = game.join(self.player, self.zombie)
        game.join(other_player, self.chicken)
        game.start()
        participation.move(1)

        with self.player_page(f"/game/{game.pk}/play", as_user="other.player") as player_page:
            self.expect(player_page.get_by_test_id("roll-dice-button")).to_be_disabled()
            self.expect(player_page.get_by_test_id("end-turn-button")).to_be_disabled()
            participation.end_turn()
            self.expect(player_page.get_by_test_id("roll-dice-button")).to_be_enabled()

    def test_displays_player_balance(self):
        device = Device.objects.create()
        game = Game.objects.create(owner=self.player, board=self.board, device=device, max_participations=1)
        participation = game.join(self.player, self.zombie)
        game.start()

        with self.player_page(f"/game/{game.pk}/play") as player_page:
            self.expect(player_page.get_by_test_id("participation-balance")).to_have_text("0 M")
            participation.balance = 1500
            participation.save()
            self.expect(player_page.get_by_test_id("participation-balance")).to_have_text("1’500 M")  # noqa: RUF001
