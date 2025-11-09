import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = "8212891702:AAF0cRwxPOa4xXMcSlKdpvk18JQBxzhU0ZA"
GAMES_URL = "https://www.mgrevolution.ru/data/games.json"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Функция получения списка игр из JSON
async def get_games():
    async with aiohttp.ClientSession() as session:
        async with session.get(GAMES_URL, ssl = False) as response:
            return await response.json()

# Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: types.Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📅 Записаться", callback_data="show_games")
    await message.answer(
        "Привет! Добро пожаловать в бота Revolution!\n"
        "Чтобы записаться, нажми кнопку.",
        reply_markup=keyboard.as_markup()
    )

# Обработчик кнопки "Записаться"
@dp.callback_query(lambda c: c.data == "show_games")
async def show_games(callback: types.CallbackQuery):
    games = await get_games()
    kb = InlineKeyboardBuilder()
    for i, game in enumerate(games):
        text = f"{game['title']} ({game['date']})"
        kb.button(text=text, callback_data=f"game_{i}")
    kb.adjust(1)
    await callback.message.answer("Выберите игру:", reply_markup=kb.as_markup())
    await callback.answer()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
