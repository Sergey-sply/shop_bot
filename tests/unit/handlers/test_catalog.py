import types
import pytest
from unittest.mock import AsyncMock

import src.bot.handlers.user.catalog as catalog_mod

pytestmark = pytest.mark.asyncio

class FakeMessage:
    def __init__(self):
        self.chat = types.SimpleNamespace(id=99)
        self.caption = None
        self.answer = AsyncMock()
        self.edit_text = AsyncMock()
        self.delete = AsyncMock()

class FakeCallback:
    def __init__(self, message: FakeMessage):
        self.message = message
        self.answer = AsyncMock()

class FakeBot:
    def __init__(self):
        self.send_message = AsyncMock()

class FakeState:
    def __init__(self):
        self.clear = AsyncMock()

class FakeCtgService:
    pass

class FakeProductService:
    pass


@pytest.fixture(autouse=True)
def patch_keyboards(monkeypatch):
    """Generate fake keyboards"""
    # CategoryListKeyboard / ProductCategoryListKeyboard
    class _KB:
        def __init__(self, *_a, **_k): pass
    monkeypatch.setattr(catalog_mod, "CategoryListKeyboard", _KB)
    monkeypatch.setattr(catalog_mod, "ProductCategoryListKeyboard", _KB)

    # InlineKeyboardBuilder()
    monkeypatch.setattr(catalog_mod, "InlineKeyboardBuilder", lambda: object())

    # combine_keyboards(...)
    monkeypatch.setattr(catalog_mod, "combine_keyboards", lambda rules, builder=None: "KB")


async def test_get_categories_hnd_success(monkeypatch):
    m = FakeMessage()
    state = FakeState()

    ctg_service = FakeCtgService()   # Create empty class S
    ctg_service.get_category_list = AsyncMock(return_value=object())

    await catalog_mod.get_categories_hnd(
        message=m, state=state, ctg_service=ctg_service
    )

    state.clear.assert_awaited_once()
    m.answer.assert_awaited_once()
    _, kwargs = m.answer.await_args
    assert kwargs.get("text") == "Выберите категорию"
    assert kwargs.get("reply_markup") == "KB"


async def test_get_categories_hnd_empty(monkeypatch):
    m = FakeMessage()
    state = FakeState()

    ctg_service = FakeCtgService()
    ctg_service.get_category_list = AsyncMock(return_value=None)

    await catalog_mod.get_categories_hnd(
        message=m, state=state, ctg_service=ctg_service
    )

    m.answer.assert_awaited_once()
    _, kwargs = m.answer.await_args
    assert "Товаров нет" in kwargs.get("text")


async def test_get_categories_clb_empty(monkeypatch):
    msg = FakeMessage()
    cb = FakeCallback(msg)

    ctg_service = FakeCtgService()
    ctg_service.get_category_list = AsyncMock(return_value=None)

    data = types.SimpleNamespace(page=1)

    await catalog_mod.get_categories_clb(
        callback=cb, callback_data=data, ctg_service=ctg_service
    )

    cb.answer.assert_awaited_once()
    _, kwargs = cb.answer.await_args
    assert "Категорий нет" in kwargs.get("text")


async def test_get_products_from_category_caption_branch(monkeypatch):
    msg = FakeMessage()
    msg.caption = "prev photo"
    cb = FakeCallback(msg)
    bot = FakeBot()

    product_service = FakeProductService()
    product_service.get_product_list_by_category_id = AsyncMock(return_value=object())  # not None

    data = types.SimpleNamespace(category_id=10, page=1)

    await catalog_mod.get_products_from_category_hnd(
        callback=cb,
        callback_data=data,
        bot=bot,
        product_service=product_service
    )

    msg.delete.assert_awaited_once()
    bot.send_message.assert_awaited_once()
    _, kwargs = bot.send_message.await_args
    assert kwargs.get("text") == "Выберите товар"
    assert kwargs.get("reply_markup") == "KB"
    assert kwargs.get("chat_id") == msg.chat.id


async def test_get_products_from_category_empty(monkeypatch):
    msg = FakeMessage()
    cb = FakeCallback(msg)
    bot = FakeBot()

    product_service = FakeProductService()
    product_service.get_product_list_by_category_id = AsyncMock(return_value=None)

    data = types.SimpleNamespace(category_id=10, page=1)

    await catalog_mod.get_products_from_category_hnd(
        callback=cb,
        callback_data=data,
        bot=bot,
        product_service=product_service
    )

    cb.answer.assert_awaited_once()
    _, kwargs = cb.answer.await_args
    assert "Товаров в выбранной категории нет" in kwargs.get("text")
