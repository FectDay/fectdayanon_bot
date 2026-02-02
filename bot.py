reply_map = {}
import asyncio
import os
import re

from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message, FSInputFile,
    InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery
)
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder


TOKEN = ""
ADMIN_ID = 0123456789


#Инициализация бота и диспетчера
bot = Bot(TOKEN)
dp = Dispatcher()

#Клавиатуры
def build_reply_kb():
    kb = ReplyKeyboardBuilder()
    kb.button(text="✉️ Написать анонимно")
    kb.button(text="ℹ️ О боте")
    kb.button(text="📢 Канал Фекта")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)

def build_inline_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Написать анонимно", callback_data="anon")],
        [InlineKeyboardButton(text="ℹ️ О боте", callback_data="about")],
        [InlineKeyboardButton(text="📢 Канал Фекта", url="https://t.me/fectday")]
    ])

def admin_kb_for(anon_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💬 Ответить", callback_data=f"reply_{anon_id}")
        ]
    ])

#Временное состояние
users_waiting = {}

#/start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    video_obj = None
    try:
        if os.path.exists(r"C:\Users\rusla\Pictures\Бригадирчикуменя.mp4"):
            video_obj = FSInputFile(r"C:\Users\rusla\Pictures\Бригадирчикуменя.mp4")
    except:
        pass

    text = (
        f"Привет, {message.from_user.first_name} 👋\n\n"
        "Ты в официальном боте анонимных сообщений FectDay.\n\n"
        "Здесь можно отправить полностью анонимное сообщение.\n\n"
        "Нажми Написать анонимно, чтобы начать."
    )

    if video_obj:
        await message.answer_video(video_obj, caption=text, reply_markup=build_inline_menu(), supports_streaming=True)
    else:
        await message.answer(text, reply_markup=build_inline_menu())

    await message.answer("Меню продублировано здесь ⬇️", reply_markup=build_reply_kb())

#Меню
@dp.callback_query(lambda c: c.data == "anon")
async def cb_anon_inline(callback: CallbackQuery):
    users_waiting[callback.from_user.id] = True
    await callback.message.answer("Напиши своё анонимное сообщение.")
    await callback.answer()

@dp.callback_query(lambda c: c.data == "about")
async def cb_about_inline(callback: CallbackQuery):
    await callback.message.answer(
        "ℹ️ О боте\n\nРазработчик: FectDay\nЯзык: Python 3+"
    )
    await callback.answer()

@dp.message(lambda m: m.text == "✉️ Написать анонимно")
async def reply_anon(message: Message):
    users_waiting[message.from_user.id] = True
    await message.answer("Напиши своё анонимное сообщение.")

@dp.message(lambda m: m.text == "ℹ️ О боте")
async def reply_about(message: Message):
    await message.answer("ℹ️ О боте\n\nРазработчик: FectDay")

@dp.message(lambda m: m.text == "📢 Канал Фекта")
async def reply_channel(message: Message):
    await message.answer("Официальный канал Фекта: https://t.me/fectday")

#Ответы админа
@dp.callback_query(lambda c: c.data and c.data.startswith("reply_"))
async def cb_admin_reply(callback: CallbackQuery):
    anon_id = int(callback.data.split("_", 1)[1])
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Только админ.", show_alert=True)
        return

    await callback.message.answer("Ответьте реплаем на это сообщение.")
    await callback.answer()

#Главный хэндлер
@dp.message()
async def handle_all(message: Message):
    uid = message.from_user.id

    #Ответ админа
    if uid == ADMIN_ID and message.reply_to_message:
        data = reply_map.get(message.reply_to_message.message_id)
        if data:
            anon_id, user_msg_id = data

            if message.text:
                await bot.send_message(anon_id, "📨 Ответ от Фекта:")
                await bot.send_message(
                    anon_id,
                    message.text,
                    entities=message.entities,
                    reply_to_message_id=user_msg_id
                )
            await message.answer("Ответ отправлен анониму.")
            return

    #Анонимка
    if users_waiting.get(uid):
        users_waiting[uid] = False

        header = (
            f"📩 Анонимное сообщение\n\n"
            f"ANON_ID:{uid}"
        )

        if message.text:
            msg = await bot.send_message(ADMIN_ID, f"{header}\n\n{message.text}", reply_markup=admin_kb_for(uid))
            reply_map[msg.message_id] = (uid, message.message_id)

        await message.answer("Сообщение отправлено анонимно ✅")
        return

#Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
