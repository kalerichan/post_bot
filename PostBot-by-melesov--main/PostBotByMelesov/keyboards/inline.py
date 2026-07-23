from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_channels_keyboard(channels):
    builder = InlineKeyboardBuilder()

    for channel in channels:
        builder.add(InlineKeyboardButton(
            text=f"📢 {channel}",
            callback_data=f"channel_{channel}"
        ))

    builder.add(InlineKeyboardButton(
        text="➕ Добавить бота в канал",
        callback_data="add_bot_to_channel"
    ))

    builder.adjust(1)
    return builder.as_markup()


def get_confirm_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Опубликовать", callback_data="publish_yes"))
    builder.add(InlineKeyboardButton(text="❌ Отменить", callback_data="publish_no"))
    builder.adjust(2)
    return builder.as_markup()