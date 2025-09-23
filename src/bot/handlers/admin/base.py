from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.callback.admin.order import AdmStartCallbackFactory
from src.bot.filters.role import RoleFilter
from src.bot.keyboards.admin.product import AdminPanelKeyboard
from src.bot.keyboards.factory import combine_keyboards

admin_panel_router = Router()
admin_panel_router.message.filter(RoleFilter(required_role="admin"))

@admin_panel_router.message(Command("admin"))
async def admin_panel_cmd(message: Message, state: FSMContext, command: CommandObject):
    await state.clear()
    keyboard_rules = [AdminPanelKeyboard()]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await message.answer(
        "Панель администратора",
        reply_markup=keyboard
    )


@admin_panel_router.callback_query(AdmStartCallbackFactory.filter())
async def admin_panel_clb(callback: CallbackQuery):

    keyboard_rules = [AdminPanelKeyboard()]
    keyboard = combine_keyboards(keyboard_rules, builder=InlineKeyboardBuilder())

    await callback.message.edit_text(
        text="Панель администратора",
        reply_markup=keyboard
    )
