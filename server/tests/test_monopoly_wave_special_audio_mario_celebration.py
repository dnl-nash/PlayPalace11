"""Wave special-audio behavior tests for Mario Celebration question-block hardware mapping."""

from server.games.monopoly.game import MonopolyGame, MonopolyOptions
from server.games.monopoly.hardware_emulation import resolve_hardware_sound_asset
from server.users.test_user import MockUser


def _start_board(board_id: str, sound_mode: str) -> MonopolyGame:
    game = MonopolyGame(
        options=MonopolyOptions(
            preset_id="classic_standard",
            board_id=board_id,
            board_rules_mode="auto",
        )
    )
    game.add_player("Host", MockUser("Host"))
    game.add_player("Guest", MockUser("Guest"))
    game.host = "Host"
    game.on_start()
    game.active_sound_mode = sound_mode
    return game


def _force_question_block_draw(game: MonopolyGame, monkeypatch) -> None:
    host = game.current_player
    assert host is not None

    host.position = 5
    monkeypatch.setattr(game, "_draw_card", lambda deck_type: "bank_dividend_50")
    rolls = iter([1, 1])
    monkeypatch.setattr("server.games.monopoly.game.random.randint", lambda a, b: next(rolls))
    game.execute_action(host, "roll_dice")


def test_mario_celebration_emits_question_block_sound_event_in_emulated_mode(monkeypatch):
    game = _start_board("mario_celebration", sound_mode="emulated")
    played: list[str] = []
    monkeypatch.setattr(game, "play_sound", lambda name, volume=100, pan=0, pitch=100: played.append(name))

    _force_question_block_draw(game, monkeypatch)
    expected_asset, expected_source = resolve_hardware_sound_asset("mario_question_block_sound")

    assert game.last_hardware_event_id == "mario_question_block_sound"
    assert game.last_hardware_event_status == "emulated"
    assert played == [expected_asset]
    assert expected_source in {"original", "placeholder"}


def test_mario_celebration_question_block_event_is_ignored_in_none_mode(monkeypatch):
    game = _start_board("mario_celebration", sound_mode="none")
    played: list[str] = []
    monkeypatch.setattr(game, "play_sound", lambda name, volume=100, pan=0, pitch=100: played.append(name))

    _force_question_block_draw(game, monkeypatch)

    assert game.last_hardware_event_id == "mario_question_block_sound"
    assert game.last_hardware_event_status == "ignored"
    assert played == []


def test_non_hardware_mario_board_does_not_emit_question_block_event(monkeypatch):
    game = _start_board("mario_movie", sound_mode="emulated")
    played: list[str] = []
    monkeypatch.setattr(game, "play_sound", lambda name, volume=100, pan=0, pitch=100: played.append(name))

    _force_question_block_draw(game, monkeypatch)

    assert game.last_hardware_event_id == ""
    assert game.last_hardware_event_status == "none"
    assert played == []
