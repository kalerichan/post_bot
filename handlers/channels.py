from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from data.db import db
from keyboards.inline import get_channels_keyboard

router = Router()


class ChannelForm(StatesGroup):
    waiting_channel_username = State()


@router.callback_query(F.data == "add_bot_to_channel")
async def add_bot_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пришлите @username канала (например: @my_channel):")
    await state.set_state(ChannelForm.waiting_channel_username)


@router.message(ChannelForm.waiting_channel_username)
async def process_channel_username(message: Message, state: FSMContext):
    channel_username = message.text.strip()

    if not channel_username.startswith('@'):
        await message.answer("Username должен начинаться с @. Попробуйте снова:")
        return

    db.add_channel(message.from_user.id, channel_username)
    await state.clear()

    channels = db.get_user_channels(message.from_user.id)
    await message.answer(f"Канал {channel_username} добавлен! Выберите канал для публикации:",
                         reply_markup=get_channels_keyboard(channels))


@router.callback_query(F.data.startswith("channel_"))
async def channel_select_handler(callback: CallbackQuery, state: FSMContext):
    channel_username = callback.data.replace("channel_", "")

    await state.update_data(selected_channel=channel_username)
    from handlers.post_creation import Form
    await state.set_state(Form.photo)

    await callback.message.answer(f"Выбран канал: {channel_username}\n\nОтправьте фото для поста или напишите 'нет':")