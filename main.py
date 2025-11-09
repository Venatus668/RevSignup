import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = "8212891702:AAF0cRwxPOa4xXMcSlKdpvk18JQBxzhU0ZA"
GAMES_URL = "https://www.mgrevolution.ru/data/games.json"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Функция получения списка игр из JSON
async def get_games():
    async with aiohttp.ClientSession() as session:
        async with session.get(GAMES_URL, ssl=False) as response:
            return await response.json()

# FSM для записи игрока
class Registration(StatesGroup):
    name = State()
    contact = State()
    role = State()
    wishes = State()

# Функция для начала регистрации
async def start_registration(message: types.Message, state: FSMContext, game_title: str):
    await state.update_data(game=game_title)
    await message.answer("Введите ваше имя или игровую кличку:")
    await state.set_state(Registration.name)

# Последовательный сбор данных
@dp.message(Registration.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Введите ссылку на ваш VK или Telegram:")
    await state.set_state(Registration.contact)

@dp.message(Registration.contact)
async def get_contact(message: types.Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await message.answer("Укажите до трех желаемых ролей(или имя персонажа, если переносите):")
    await state.set_state(Registration.role)

@dp.message(Registration.role)
async def get_role(message: types.Message, state: FSMContext):
    await state.update_data(role=message.text)
    await message.answer("Введите пожелания и комментарии (если есть, в том числе - по существующей квенте):")
    await state.set_state(Registration.wishes)

@dp.message(Registration.wishes)
async def get_wishes(message: types.Message, state: FSMContext):
    await state.update_data(wishes=message.text)
    data = await state.get_data()

    # Формируем красивое сообщение об успешной записи
    confirmation_text = (
        f"✅ <b>Вы успешно записаны на игру!</b>\n\n"
        f"🎲 <b>Игра:</b> {data['game']}\n"
        f"🧍 <b>Имя / кличка:</b> {data['name']}\n"
        f"🔗 <b>Контакт:</b> {data['contact']}\n"
        f"🎭 <b>Роль / персонаж:</b> {data['role']}\n"
        f"💬 <b>Пожелания:</b> {data['wishes']}\n\n"
        f"Спасибо за регистрацию! Мы свяжемся с вами для уточнения деталей."
    )

    await message.answer(confirmation_text, parse_mode="HTML")
    await state.clear()

# Обработчик команды /start
@dp.message(CommandStart())
async def start_command(message: types.Message):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📅 Записаться", callback_data="show_games")
    await message.answer(
        "Привет! Добро пожаловать в бота Revolution!\n"
        "Чтобы записаться, нажми на кнопку ниже.",
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

# Обработчик выбора конкретной игры
@dp.callback_query(lambda c: c.data.startswith("game_"))
async def choose_game(callback: types.CallbackQuery, state: FSMContext):
    games = await get_games()
    index = int(callback.data.split('_')[1])
    game = games[index]
    await callback.message.answer(f"Вы выбрали игру: <b>{game['title']}</b>", parse_mode="HTML")
    await start_registration(callback.message, state, game['title'])
    await callback.answer()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
