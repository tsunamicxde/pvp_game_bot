from config import BOT_TOKEN, host, port, db_name, user, password

import logging
import psycopg2
import random

from aiogram import types, executor, Bot, Dispatcher

from aiogram.types.message import ContentType
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)
dp.middleware.setup(LoggingMiddleware())

conn = psycopg2.connect(
    host=host,
    port=port,
    dbname=db_name,
    user=user,
    password=password
)
cursor = conn.cursor()

with open('create_users_table.sql', 'r') as sql_config:
    create_table_query = sql_config.read()

cursor.execute(create_table_query)

conn.commit()

all_types = {"1": "👊", "2": "✌️", "3": "🫳"}


def call_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    find_opponent = types.InlineKeyboardButton("Найти соперника", callback_data="find_opponent")
    play_with_bot = types.InlineKeyboardButton("Сыграть с ботом", callback_data="play_with_bot")
    rules = types.InlineKeyboardButton("Правила игры", callback_data="rules")
    markup.add(find_opponent, play_with_bot, rules)
    return markup


def play_menu():
    markup = types.InlineKeyboardMarkup(row_width=1)
    for key, value in all_types.items():
        button = types.InlineKeyboardButton(value, callback_data=key)
        markup.add(button)
    return markup


@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.chat.id

    user_url = f'tg://openmessage?user_id={user_id}'

    keyboard = call_menu()
    await message.reply("Привет! Я - бот, который найдёт тебе соперника для игры в камень-ножницы-бумага",
                        reply_markup=keyboard)

    # async with state.proxy() as data:
    #     data['current_step'] = 1

    try:
        insert_query = '''
                INSERT INTO users (user_id, user_url)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET user_id = EXCLUDED.user_id, user_url = EXCLUDED.user_url
                RETURNING user_id;
            '''

        cursor.execute(insert_query, (user_id, user_url))
        conn.commit()
    except psycopg2.Error:
        conn.rollback()
        await message.reply("Что-то пошло не так")


@dp.callback_query_handler(lambda callback_query: True)
async def callback(call, state: FSMContext):
    user_id = call.message.chat.id
    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

    if call.data == "play_with_bot":
        keyboard = play_menu()
        await bot.send_message(call.message.chat.id, "Выберите действие",
                               reply_markup=keyboard)
    elif call.data in all_types.keys():
        await bot.send_message(call.message.chat.id, f"Вы: {str(all_types[call.data])}")
        random_number = random.randint(1, 3)
        await bot.send_message(call.message.chat.id, f"Бот: {str(all_types[str(random_number)])}")
        if str(random_number) == call.data:
            keyboard = play_menu()
            await bot.send_message(call.message.chat.id, "Вы сыграли в ничью! Выберите действие: ",
                                   reply_markup=keyboard)
        elif str(random_number) == "1" and call.data == "2":
            keyboard = play_menu()
            await bot.send_message(call.message.chat.id, "Вы проиграли! Выберите действие: ",
                                   reply_markup=keyboard)
        elif str(random_number) == "1" and call.data == "3":
            keyboard = play_menu()
            await bot.send_message(call.message.chat.id, "Вы выиграли! Выберите действие: ",
                                   reply_markup=keyboard)
        elif str(random_number) == "2" and call.data == "1":
            keyboard = play_menu()
            await bot.send_message(call.message.chat.id, "Вы выиграли! Выберите действие: ",
                                   reply_markup=keyboard)
        elif str(random_number) == "2" and call.data == "3":
            keyboard = play_menu()
            await bot.send_message(call.message.chat.id, "Вы проиграли! Выберите действие: ",
                                   reply_markup=keyboard)
        elif str(random_number) == "3" and call.data == "1":
            print(random_number, call.data)
            keyboard = play_menu()
            await bot.send_message(call.message.chat.id, "Вы проиграли! Выберите действие: ",
                                   reply_markup=keyboard)
        elif str(random_number) == "3" and call.data == "2":
            keyboard = play_menu()
            await bot.send_message(call.message.chat.id, "Вы выиграли! Выберите действие: ",
                                   reply_markup=keyboard)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

