from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.bot.keyboards.start_kb import get_main_kb

start_router = Router()

@start_router.message(Command("start"))
async def start_cmd(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    keyboard = get_main_kb()
    await message.answer(
        "Приветственное сообщение",
        reply_markup=keyboard
    )
