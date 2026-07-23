import json
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN, ADMIN_ID

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

DATA_FILE = "data.json"

# ================== РАБОТА С ДАННЫМИ ==================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"channels": [], "posts": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# ================== СОСТОЯНИЯ ==================
class PostCreation(StatesGroup):
    waiting_for_channel = State()
    waiting_for_text = State()
    waiting_for_photo = State()
    waiting_for_button_text = State()
    waiting_for_button_url = State()
    confirm_post = State()

# ================== КЛАВИАТУРЫ ==================
def main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Создать пост", callback_data="create_post")],
        [InlineKeyboardButton(text="📂 Мои каналы", callback_data="my_channels")],
        [InlineKeyboardButton(text="➕ Добавить канал", callback_data="add_channel")],
        [InlineKeyboardButton(text="❌ Удалить канал", callback_data="remove_channel")]
    ])
    return keyboard

def channel_list_keyboard(channels):
    keyboard = []
    for channel in channels:
        keyboard.append([InlineKeyboardButton(text=f"📢 {channel}", callback_data=f"select_channel_{channel}")])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ================== ОБРАБОТЧИКИ ==================
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет доступа к этому боту.")
        return
    await message.answer(
        "🌸 Привет! Я бот-конструктор постов для каналов.\n\n"
        "Что хочешь сделать?",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🌸 Что хочешь сделать?",
        reply_markup=main_menu()
    )
    await callback.answer()

@dp.callback_query(F.data == "add_channel")
async def add_channel(callback: types.CallbackQuery, state: FSMContext):
    data = load_data()
    channels = data.get("channels", [])
    if len(channels) >= 10:
        await callback.message.edit_text("❌ Максимум 10 каналов. Удалите один, чтобы добавить новый.")
        await callback.answer()
        return
    await callback.message.edit_text(
        "📢 Отправь мне **username** канала (например, @my_channel) или его **ID** (число).\n\n"
        "⚠️ Убедись, что бот добавлен в канал как **администратор**!"
    )
    await state.set_state(PostCreation.waiting_for_channel)
    await callback.answer()

@dp.message(PostCreation.waiting_for_channel)
async def process_channel_add(message: types.Message, state: FSMContext):
    channel = message.text.strip()
    if not channel:
        await message.answer("❌ Введи корректный username или ID канала.")
        return
    data = load_data()
    if channel in data.get("channels", []):
        await message.answer(f"❌ Канал {channel} уже добавлен.")
        await state.clear()
        await message.answer("🌸 Что хочешь сделать?", reply_markup=main_menu())
        return
    data["channels"].append(channel)
    save_data(data)
    await message.answer(f"✅ Канал {channel} добавлен!")
    await state.clear()
    await message.answer("🌸 Что хочешь сделать?", reply_markup=main_menu())

@dp.callback_query(F.data == "remove_channel")
async def remove_channel(callback: types.CallbackQuery):
    data = load_data()
    channels = data.get("channels", [])
    if not channels:
        await callback.message.edit_text("❌ Нет добавленных каналов.")
        await callback.answer()
        return
    keyboard = []
    for channel in channels:
        keyboard.append([InlineKeyboardButton(text=f"❌ {channel}", callback_data=f"remove_{channel}")])
    keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")])
    await callback.message.edit_text("Выбери канал для удаления:", reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
    await callback.answer()

@dp.callback_query(F.data.startswith("remove_"))
async def confirm_remove(callback: types.CallbackQuery):
    channel = callback.data.replace("remove_", "")
    data = load_data()
    if channel in data["channels"]:
        data["channels"].remove(channel)
        save_data(data)
        await callback.message.edit_text(f"✅ Канал {channel} удалён!")
    else:
        await callback.message.edit_text("❌ Канал не найден.")
    await callback.answer()
    await callback.message.answer("🌸 Что хочешь сделать?", reply_markup=main_menu())

@dp.callback_query(F.data == "my_channels")
async def show_channels(callback: types.CallbackQuery):
    data = load_data()
    channels = data.get("channels", [])
    if not channels:
        await callback.message.edit_text("❌ Нет добавленных каналов.\n\n➕ Нажми «Добавить канал», чтобы начать.")
        await callback.answer()
        return
    text = "📋 **Мои каналы:**\n\n" + "\n".join([f"• {ch}" for ch in channels])
    await callback.message.edit_text(text, reply_markup=channel_list_keyboard(channels))
    await callback.answer()

@dp.callback_query(F.data == "create_post")
async def start_create_post(callback: types.CallbackQuery, state: FSMContext):
    data = load_data()
    channels = data.get("channels", [])
    if not channels:
        await callback.message.edit_text("❌ Сначала добавь канал через «➕ Добавить канал».")
        await callback.answer()
        return
    await callback.message.edit_text(
        "📢 **Выбери канал для публикации:**",
        reply_markup=channel_list_keyboard(channels)
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("select_channel_"))
async def process_channel_selection(callback: types.CallbackQuery, state: FSMContext):
    channel = callback.data.replace("select_channel_", "")
    await state.update_data(channel=channel)
    await callback.message.edit_text(
        f"📝 **Выбран канал:** {channel}\n\n"
        "Теперь отправь **текст** поста (можно с эмодзи).\n"
        "Если хочешь добавить фото, отправь его после текста."
    )
    await state.set_state(PostCreation.waiting_for_text)
    await callback.answer()

@dp.message(PostCreation.waiting_for_text)
async def process_post_text(message: types.Message, state: FSMContext):
    if message.text and message.text.startswith("/"):
        await message.answer("❌ Команды недоступны во время создания поста. Нажми /cancel, чтобы отменить.")
        return
    await state.update_data(text=message.text or "")
    await state.update_data(photo=message.photo[-1].file_id if message.photo else None)
    await message.answer(
        "📝 Текст сохранён!\n\n"
        "Теперь добавь **кнопку** (если нужно).\n"
        "Введи **текст кнопки** или нажми «Пропустить»."
    )
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏭️ Пропустить кнопку", callback_data="skip_button")]
    ])
    await message.answer("Введи текст кнопки (например, «Перейти на сайт»):", reply_markup=keyboard)
    await state.set_state(PostCreation.waiting_for_button_text)

@dp.callback_query(F.data == "skip_button")
async def skip_button(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(button_text=None, button_url=None)
    await callback.message.edit_text("⏭️ Кнопка пропущена.")
    await confirm_post(callback.message, state)
    await callback.answer()

@dp.message(PostCreation.waiting_for_button_text)
async def process_button_text(message: types.Message, state: FSMContext):
    if message.text and message.text.startswith("/"):
        await message.answer("❌ Команды недоступны. Нажми /cancel, чтобы отменить.")
        return
    await state.update_data(button_text=message.text)
    await message.answer("🔗 Теперь введи **ссылку** для кнопки (полный URL, начинается с http:// или https://):")
    await state.set_state(PostCreation.waiting_for_button_url)

@dp.message(PostCreation.waiting_for_button_url)
async def process_button_url(message: types.Message, state: FSMContext):
    if message.text and message.text.startswith("/"):
        await message.answer("❌ Команды недоступны. Нажми /cancel, чтобы отменить.")
        return
    url = message.text.strip()
    if not url.startswith(("http://", "https://")):
        await message.answer("❌ Ссылка должна начинаться с http:// или https://. Попробуй снова.")
        return
    await state.update_data(button_url=url)
    await confirm_post(message, state)

async def confirm_post(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = data.get("text", "Без текста")
    photo = data.get("photo")
    button_text = data.get("button_text")
    button_url = data.get("button_url")
    channel = data.get("channel", "Не выбран")

    preview = f"📢 **Предпросмотр поста**\n\n**Канал:** {channel}\n\n**Текст:**\n{text}"
    if button_text and button_url:
        preview += f"\n\n🔘 **Кнопка:** {button_text} → {button_url}"
    else:
        preview += "\n\n🔘 Без кнопки"

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать", callback_data="publish_post")],
        [InlineKeyboardButton(text="✏️ Редактировать текст", callback_data="edit_text")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
    ])

    if photo:
        await message.answer_photo(photo=photo, caption=preview, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(preview, reply_markup=keyboard, parse_mode="Markdown")

@dp.callback_query(F.data == "edit_text")
async def edit_text(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📝 Отправь новый текст поста (или /cancel, чтобы отменить).")
    await state.set_state(PostCreation.waiting_for_text)
    await callback.answer()

@dp.callback_query(F.data == "publish_post")
async def publish_post(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    channel = data.get("channel")
    text = data.get("text", "Без текста")
    photo = data.get("photo")
    button_text = data.get("button_text")
    button_url = data.get("button_url")

    try:
        if button_text and button_url:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=button_text, url=button_url)]
            ])
        else:
            keyboard = None

        if photo:
            await bot.send_photo(chat_id=channel, photo=photo, caption=text, reply_markup=keyboard, parse_mode="Markdown")
        else:
            await bot.send_message(chat_id=channel, text=text, reply_markup=keyboard, parse_mode="Markdown")

        await callback.message.edit_text("✅ **Пост опубликован!** 🎉")
        await callback.answer()
        await state.clear()
        await callback.message.answer("🌸 Что хочешь сделать дальше?", reply_markup=main_menu())
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка при публикации: {str(e)}\n\nПроверь, что бот добавлен в канал как администратор.")
        await callback.answer()

@dp.message(Command("cancel"))
async def cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Действие отменено.", reply_markup=main_menu())

# ================== ЗАПУСК ==================
async def main():
    logging.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
