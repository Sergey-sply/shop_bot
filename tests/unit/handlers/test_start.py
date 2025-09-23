import pytest
from unittest.mock import AsyncMock

import src.bot.handlers.user.start as start_mod

pytestmark = pytest.mark.asyncio

class FakeState:
    def __init__(self): self.clear = AsyncMock()

class FakeMessage:
    def __init__(self):
        self.answer = AsyncMock()

@pytest.fixture(autouse=True)
def patch_keyboard(monkeypatch):
    monkeypatch.setattr(start_mod, "get_main_kb", lambda: "KB")

async def test_start_cmd_sends_greeting_and_clears_state():
    m = FakeMessage()
    state = FakeState()

    await start_mod.start_cmd(message=m, command=None, state=state)

    state.clear.assert_awaited_once()
    m.answer.assert_awaited_once_with("Приветственное сообщение", reply_markup="KB")