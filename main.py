import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

BOT_TOKEN = "8212891702:AAF0cRwxPOa4xXMcSlKdpvk18JQBxzhU0ZA"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.answer(
        "Привет! Добро пожаловать в бота Revolution!\n"
        "Чтобы записаться, выбери одну из доступных игр."
    )

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
