import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
from dotenv import load_dotenv
import os
# Загрузка переменных окружения из .env файла
load_dotenv()
API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
# Проверка, что токен был загружен
if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не установлен в .env файле.")
# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
# Загрузка модели и токенизатора
model_name = "EleutherAI/gpt-neo-125M"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPTNeoForCausalLM.from_pretrained(model_name)
async def generate_response(prompt):
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(inputs['input_ids'], max_length=150, num_return_sequences=1)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response
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
async def handle_callback_query(callback_query: types.CallbackQuery):
    if callback_query.data == "book_appointment":
        await callback_query.answer("Вы выбрали запись к врачу. Пожалуйста, свяжитесь с нашей службой поддержки для назначения.")
        await bot.send_message(callback_query.from_user.id, "Чтобы записаться к врачу, позвоните по телефону: +7 (123) 456-78-90.")
    elif callback_query.data == "online_consultation":
        await callback_query.answer("Вы выбрали консультацию онлайн.")
        await bot.send_message(callback_query.from_user.id, "Вы можете получить консультацию, заполнив форму на нашем сайте.")
    elif callback_query.data == "beauty_health_tips":
        await callback_query.answer("Вы выбрали советы по красоте и здоровью.")
        tips = "Каждый день новые упражнения на нашем канале - https://t.me/+BokVVpRyGsFhNmIy."
        await bot.send_message(callback_query.from_user.id, tips)
    elif callback_query.data == "actions":
        await callback_query.answer("Акции на сегодня.")
        await bot.send_message(callback_query.from_user.id, "Записавшись на УЗИ сегодня, получите скидку 10%!")
    elif callback_query.data == "clinics_places":
        await callback_query.answer("Ищите адреса клиник ?")
        tips = "Клиника на Партизанской: Партизанская, 74, Клиника на Красных Воротах: Красные Ворота, д.5."
        await bot.send_message(callback_query.from_user.id, tips)
    elif callback_query.data == "doctors":
        await callback_query.answer("О наших докторах :")
        tips = "Вся информация о наших докторах на сайте: prodoctorov.ru"
        await bot.send_message(callback_query.from_user.id, tips)
@dp.message()
async def handle_question(message: types.Message):
    user_question = message.text
    response = await generate_response(user_question)
    await message.answer(response)
if __name__ == '__main__':
    # Запуск бота
    try:
        asyncio.run(dp.start_polling(bot))  # Передаем объект бота в start_polling
    except Exception as e:
        print(f"An error occurred: {e}")
