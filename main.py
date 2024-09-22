import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, StateFilter
from aiogram import F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в .env файле.")
# Настройка логирования
logging.basicConfig(level=logging.INFO)
# Инициализация бота и диспетчера
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=storage)


# Определение состояний
class Form(StatesGroup):
    waiting_for_doctor = State()
    waiting_for_date = State()
    waiting_for_time = State()


@dp.message(Command("start"))
async def start_command(message: types.Message):
    # Создание клавиатуры с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Запись к врачу", callback_data="book_appointment"),
            InlineKeyboardButton(text="Консультация онлайн", callback_data="online_consultation"),
        ],
        [
            InlineKeyboardButton(text="Советы по красоте и здоровью", callback_data="beauty_health_tips"),
            InlineKeyboardButton(text="Акции", callback_data="actions"),
        ],
        [
            InlineKeyboardButton(text="Офисы Клиники", callback_data="clinics_places"),
            InlineKeyboardButton(text="Наши врачи", callback_data="doctors"),
        ]
    ])
    await message.answer("Добрый день! Пожалуйста, выберите один из вариантов:", reply_markup=keyboard)


@dp.callback_query()
async def handle_callback_query(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "book_appointment":
        await callback_query.answer("Вы выбрали запись к врачу.")
        await bot.send_message(callback_query.from_user.id, "К какому врачу хотите записаться?")
        await state.set_state(Form.waiting_for_doctor)  # Устанавливаем состояние ожидания врача
    elif callback_query.data == "online_consultation":
        await callback_query.answer("Вы выбрали консультацию онлайн.")
        await bot.send_message(callback_query.from_user.id,
                               "Вы можете получить консультацию, заполнив форму на нашем сайте.")
    elif callback_query.data == "beauty_health_tips":
        await callback_query.answer("Вы выбрали советы по красоте и здоровью.")
        tips = "Каждый день новые упражнения на нашем канале - https://t.me/+BokVVpRyGsFhNmIy."
        await bot.send_message(callback_query.from_user.id, tips)
    elif callback_query.data == "actions":
        await callback_query.answer("Акции на сегодня.")
        await bot.send_message(callback_query.from_user.id, "Записавшись на УЗИ сегодня, получите скидку 10%!")
    elif callback_query.data == "clinics_places":
        await callback_query.answer("Ищите адреса клиник?")
        tips = "Клиника на Партизанской: Партизанская, 74, Клиника на Красных Воротах: Красные Ворота, д.5."
        await bot.send_message(callback_query.from_user.id, tips)
    elif callback_query.data == "doctors":
        await callback_query.answer("О наших докторах:")
        tips = "Вся информация о наших докторах на сайте: prodoctorov.ru"
        await bot.send_message(callback_query.from_user.id, tips)


# Получение врача
@dp.message(StateFilter(Form.waiting_for_doctor))
async def process_doctor(message: types.Message, state: FSMContext):
    await state.update_data(doctor=message.text)
    await state.set_state(Form.waiting_for_date)
    await message.answer("Какого числа хотите записаться? (например, 25)")


# Получение даты
@dp.message(StateFilter(Form.waiting_for_date))
async def process_date(message: types.Message, state: FSMContext):
    await state.update_data(date=message.text)
    await state.set_state(Form.waiting_for_time)
    await message.answer("Во сколько хотите записаться? (например, 12)")


# Получение времени
@dp.message(StateFilter(Form.waiting_for_time))
async def process_time(message: types.Message, state: FSMContext):
    await state.update_data(time=message.text)
    data = await state.get_data()
    doctor = data.get('doctor')
    date = data.get('date')
    time = data.get('time')
    await message.answer(f"Вы записаны к {doctor}y {date} числа в {time} часов.")
    await state.clear()  # Завершение состояния


if __name__ == '__main__':
    # Запуск бота
    try:
        asyncio.run(dp.start_polling(bot))  # Передаем объект бота в start_polling
    except Exception as e:
        print(f"An error occurred: {e}")
