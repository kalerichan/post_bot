import re
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from data.db import db
from keyboards.inline import get_confirm_keyboard

router = Router()


class Form(StatesGroup):
    photo = State()
    text = State()
    button = State()


@router.message(Form.photo)
async def process_photo(message: Message, state: FSMContext):
    if message.text and message.text.lower() == 'нет':
        await state.update_data(photo=None)
        await state.set_state(Form.text)
        await message.answer("Отправьте текст для поста или напишите 'нет':")
    elif message.photo:
        await state.update_data(photo=message.photo[-1].file_id)
        await state.set_state(Form.text)
        await message.answer("Отправьте текст для поста или напишите 'нет':")
    else:
        await message.answer("Отправьте фото или напишите 'нет':")


@router.message(Form.text)
async def process_text(message: Message, state: FSMContext):
    if message.text and message.text.lower() == 'нет':
        await state.update_data(text="")
        await state.set_state(Form.button)
        await message.answer("Укажите данные для кнопки в формате [Текст + ссылка] или напишите 'нет':")
    elif message.text:
        await state.update_data(text=message.text)
        await state.set_state(Form.button)
        await message.answer("Укажите данные для кнопки в формате [Текст + ссылка] или напишите 'нет':")
    else:
        await message.answer("Отправьте текст или напишите 'нет':")


@router.message(Form.button)
async def process_button(message: Message, state: FSMContext):
    if message.text and message.text.lower() == 'нет':
        await state.update_data(button_text=None, button_url=None)
        await show_preview(message, state)
    elif message.text:
        match = re.match(r'\[(.+?) \+ (.+?)\]', message.text)
        if match:
            button_text = match.group(1)
            button_url = match.group(2)
            await state.update_data(button_text=button_text, button_url=button_url)
            await show_preview(message, state)
        else:
            await message.answer("Неверный формат. Используйте: [Текст + ссылка]")
    else:
        await message.answer("Укажите данные для кнопки или напишите 'нет':")


async def show_preview(message: Message, state: FSMContext):
    data = await state.get_data()

    preview_text = "📋 Превью поста:\n\n"

    if data.get('photo'):
        preview_text += "🖼️ Есть фото\n"
    else:
        preview_text += "🖼️ Нет фото\n"

    if data.get('text'):
        preview_text += f"📝 Текст: {data['text']}\n"
    else:
        preview_text += "📝 Нет текста\n"

    if data.get('button_text') and data.get('button_url'):
        preview_text += f"🔘 Кнопка: {data['button_text']} -> {data['button_url']}\n"
    else:
        preview_text += "🔘 Нет кнопки\n"

    preview_text += f"📢 Канал: {data['selected_channel']}\n\n"
    preview_text += "Опубликовать пост?"

    db.save_draft_post(message.from_user.id, data)

    await message.answer(preview_text, reply_markup=get_confirm_keyboard())


@router.callback_query(F.data == "publish_yes")
async def publish_handler(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()

    if 'selected_channel' not in data:
        await callback.message.answer("❌ Ошибка: канал не выбран")
        await state.clear()
        return

    try:
        keyboard = None
        if data.get('button_text') and data.get('button_url'):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=data['button_text'], url=data['button_url'])
            ]])

        channel_username = data['selected_channel']
        text = data.get('text', '')
        photo = data.get('photo')

        if not text and not photo:
            await callback.message.answer("❌ Ошибка: пост не может быть пустым (нет текста и фото)")
            return

        if photo:
            await bot.send_photo(
                chat_id=channel_username,
                photo=photo,
                caption=text if text else None,
                reply_markup=keyboard
            )
        else:
            await bot.send_message(
                chat_id=channel_username,
                text=text if text else " ",
                reply_markup=keyboard
            )

        await callback.message.answer("✅ Пост успешно опубликован!")

    except Exception as e:
        await callback.message.answer(
            f"❌ Ошибка публикации: {str(e)}\n\nУбедитесь что:\n1. Бот добавлен в канал как администратор\n2. Боту выданы все права\n3. Канал существует")

    await state.clear()

    user_id = callback.from_user.id
    from data.db import db
    from keyboards.inline import get_channels_keyboard

    channels = db.get_user_channels(user_id)

    if channels:
        await callback.message.answer(
            "Выберите канал для публикации:",
            reply_markup=get_channels_keyboard(channels)
        )
    else:
        await callback.message.answer(
            "Вы еще не добавили меня ни в один канал. Пригласите меня в канал как администратора и выдайте все права, затем нажмите кнопку ниже:",
            reply_markup=get_channels_keyboard([])
        )


@router.callback_query(F.data == "publish_no")
async def cancel_publish_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Публикация отменена.")

    user_id = callback.from_user.id
    from data.db import db
    from keyboards.inline import get_channels_keyboard

    channels = db.get_user_channels(user_id)

    if channels:
        await callback.message.answer(
            "Выберите канал для публикации:",
            reply_markup=get_channels_keyboard(channels)
        )
    else:
        await callback.message.answer(
            "Вы еще не добавили меня ни в один канал. Пригласите меня в канал как администратора и выдайте все права, затем нажмите кнопку ниже:",
            reply_markup=get_channels_keyboard([])
        )