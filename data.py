import random

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


TOKEN_API = "6341860132:AAHeV2AAFyVZqNK73nAtbnG58GGvYRuBBpo"

bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start']) # что происходит при команде старт
async def begin(message: types.Message):
      markup = InlineKeyboardMarkup() # хрень, без которой не работает inline кнопки
      # список кнопок
      random_anime=InlineKeyboardButton("Хачу аниме", callback_data="random_anime")
      anime_list=InlineKeyboardButton("Просмотренные", callback_data="anime_list")
      see_anime = InlineKeyboardButton("Список посмотреть", callback_data="see_anime")
      add_anime_list=InlineKeyboardButton("Добавить в список", callback_data="add_anime_list")
      # добавление самих кнопок
      markup.add(anime_list,add_anime_list)
      markup.add(random_anime, see_anime)
      await bot.send_message(message.chat.id, "Чего желаем?", reply_markup=markup) #отправка сообщения с кнопками


# что происходит при нажатии кнопки "Просмотренные"
@dp.callback_query_handler(lambda c: c.data == "anime_list")
async def show_list(call: types.callback_query):
      # открытие списка для чтение и вывод его
      anime_file = open('list.txt','r', encoding="utf-8")
      anime_list = anime_file.read()
      await bot.answer_callback_query(call.id)
      await bot.send_message(call.message.chat.id, anime_list) # бот отправляет список
      anime_file.close()


@dp.callback_query_handler(lambda c: c.data=="see_anime")
async def show_see(call: types.callback_query):
      anime_file = open('see.txt', 'r', encoding="utf-8")
      anime_list = anime_file.read()
      await bot.answer_callback_query(call.id)
      await bot.send_message(call.message.chat.id, anime_list)
      anime_file.close()

#Выдаёт рандомное аниме из списка
@dp.callback_query_handler(lambda c: c.data=="random_anime")
async def give_random(call: types.callback_query):
      # открытие файла и его преобразование в список
      anime_file = open('see.txt', 'r', encoding="utf-8")
      anime_text=anime_file.read()
      list_anime= anime_text.split('\n')
      random_anime = random.choice(list_anime) # выбор рандомного элемента списка
      #print(len(list_anime))
      await bot.send_message(call.message.chat.id, random_anime) # отправка результата
      anime_file.close()
#
# @dp.callback_query_handler(lambda c: c.data == "btn_back")
# async def begin(message: types.Message):
#       markup = InlineKeyboardMarkup()
#       random_anime=InlineKeyboardButton("Хачу аниме", callback_data="random_anime")
#       anime_list=InlineKeyboardButton("Просмотренные", callback_data="anime_list")
#       see_anime = InlineKeyboardButton("Список посмотреть", callback_data="see_anime")
#       add_anime_list=InlineKeyboardButton("Добавить в список", callback_data="add_anime_list")
#       markup.add(anime_list,add_anime_list)
#       markup.add(random_anime, see_anime)
#       await bot.send_message(message.chat.id, "Чего желаем?", reply_markup=markup)

def BOT():
    executor.start_polling(dp)



