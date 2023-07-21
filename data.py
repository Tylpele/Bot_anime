import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


TOKEN_API = ""

storage = MemoryStorage()
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start']) # что происходит при команде старт
async def begin(message: types.Message):
      await message.reply("/watched_list - список просмотренных тайтлов \n"
                          "/will_see - список запланированных тайтлов \n"
                          "/random_anime - случайное аниме из запланированных \n"
                          "/count_watched - число просмотренных тайтлов \n"
                          "/count_will_see - число запланированных тайтлов \n"
                          "/add_watched - добавить в просмотренные \n"
                          "/add_will_see - добавить в желаемые \n")



@dp.message_handler(commands=["watched_list"])
async def show_watched_list(message: types.Message):
      anime_file = open('list.txt', 'r', encoding="utf-8")
      anime_list = anime_file.read()
      await message.reply(anime_list)
      anime_file.close()


@dp.message_handler(commands=["will_see"])
async def show_will_see(message: types.Message):
      anime_file = open('see.txt', 'r', encoding="utf-8")
      anime_list = anime_file.read()
      await message.reply(anime_list)
      anime_file.close()


@dp.message_handler(commands=["random_anime"]) #!!!Возможно сюда приделать кнопки "добавить в просмотренное" и "ещё"
async def give_random_anime(message: types.Message):
      anime_file = open('see.txt', 'r', encoding="utf-8")
      anime_text=anime_file.read()
      list_anime= anime_text.split('\n')
      random_anime = random.choice(list_anime)
      await message.reply(random_anime)
      anime_file.close()


@dp.message_handler(commands=["count_watched"])
async def count_watched_anime(message: types.Message):
      anime_file = open('list.txt', 'r', encoding="utf-8")
      anime_list = anime_file.read()
      anime_list = anime_list.split(";")
      await message.reply(len(anime_list)-1)
      anime_file.close()


@dp.message_handler(commands=["count_will_see"])
async def count_will_see_anime(message: types.Message):
      anime_file = open('see.txt', 'r', encoding="utf-8")
      anime_text=anime_file.read()
      list_anime= anime_text.split('\n')
      await message.reply(len(list_anime))
      anime_file.close()



class Add_in_list(StatesGroup):
      waiting_add_wached = State()
      waiting_add_will_see = State()

@dp.message_handler(commands=["add_watched"])
async def state_add_watched(message: types.Message, state: FSMContext):
      await message.reply("Какое аниме я посмотрел?")
      await state.set_state(Add_in_list.waiting_add_wached.state)

@dp.message_handler(state=Add_in_list.waiting_add_wached)
async def add_watched(message: types.Message, state: FSMContext):
      await state.update_data(new_anime = message.text, encoding="utf-8")
      new_anime=message.text+"; "
      with open('list.txt', 'a+', encoding="utf-8") as anime_file:
            anime_file.write(f'{new_anime}')
      await message.answer(f"Записано")
      await state.finish()


@dp.message_handler(commands=["add_will_see"])
async def state_add_will_see(message: types.Message, state: FSMContext):
      await message.reply("Какое аниме добавить?")
      await state.set_state(Add_in_list.waiting_add_will_see)

@dp.message_handler(state=Add_in_list.waiting_add_will_see)
async def add_will_see(message: types.Message, state: FSMContext):
      await state.update_data(new_anime = message.text, encoding ="utf-8")
      new_anime = message.text+"\n"
      with open('see.txt', 'a+', encoding="utf-8") as anime_file:
            anime_file.write(f'{new_anime}')
      await message.answer(f"Записано")
      await state.finish()

def BOT():
    executor.start_polling(dp)



