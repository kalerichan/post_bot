from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from data.db import db
from keyboards.inline import get_channels_keyboard

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    channels = db.get_user_channels(user_id)

    if channels:
        await message.answer(
            "Выберите канал для публикации:",
            reply_markup=get_channels_keyboard(channels)
        )
    else:
        await message.answer(
            "Вы еще не добавили меня ни в один канал. Пригласите меня в канал как администратора и выдайте все права, затем нажмите кнопку ниже:",
            reply_markup=get_channels_keyboard([])
        )