import os

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

class UserStates(StatesGroup):
    UserPending = State()
    UserSendingMessage = State()

bot = Bot(token = os.environ.get("ANON_BOT_TOKEN"), parse_mode="html")
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage = storage)


bot_link = os.environ.get("BOT_USERNAME") or "anon_simple_bot"

@dispatcher.message_handler(commands = ["start"], state = "*")
async def start(message: types.Message, state: FSMContext):
    sender_data = message.get_args()
    if not sender_data:
        await message.answer(f"Привет! Ты можешь отправлять анонимные сообщения\n"
                           f"получив ссылку от другого человека, или ты сам можешь получать анонимные сообщения\n" 
                           f"отправив другому эту ссылку: t.me/{bot_link}?start={message.from_user.id}\n")
    else:
        await state.update_data(sender_id = sender_data)
        await UserStates.UserSendingMessage.set()
        await message.answer(f"Привет, ты можешь отправить анонимное сообщение человеку,\n"
                            f"который отправил тебе эту ссылку, или ты сам можешь получать анонимные сообщения,\n"  
                            f"отправив другому эту ссылку: t.me/{bot_link}?start={message.from_user.id}\n")
        
@dispatcher.message_handler(content_types=["text"], state = UserStates.UserSendingMessage)
async def send_anonymus_text(message: types.Message, state: FSMContext):
    sender_id = await state.get_data()
    await bot.send_message(sender_id.get("sender_id"), f"У тебя новое анонимное сообщение!\n {message.text}")
    await message.answer("Анонимное сообщение успешно отправлено!")
    await UserStates.UserPending.set()

@dispatcher.message_handler(content_types=types.ContentType.STICKER, state = UserStates.UserSendingMessage)
async def send_anonymus_sticker(message: types.Message, state: FSMContext):
    sender_id = await state.get_data()
    await bot.send_message(sender_id.get("sender_id"), f"У тебя новое анонимное сообщение!\n")
    await bot.send_sticker(sender_id.get("sender_id"), message.sticker.file_id)
    await message.answer("Анонимное сообщение успешно отправлено!")
    await UserStates.UserPending.set()

if __name__ == "__main__":
    executor.start_polling(dispatcher, skip_updates = True)