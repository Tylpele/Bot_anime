import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

TOKEN_API = "6341860132:AAHeV2AAFyVZqNK73nAtbnG58GGvYRuBBpo"

storage = MemoryStorage() # хрень, которая даёт доступ машине состояний к оперативке
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])  # что происходит при команде старт
async def begin(message: types.Message):
    #приветственная менюшка
    await message.reply("/watched_list - список просмотренных тайтлов \n"
                        "/will_see - список запланированных тайтлов \n"
                        "/random_anime - случайное аниме из запланированных \n"
                        "/count_watched - число просмотренных тайтлов \n"
                        "/count_will_see - число запланированных тайтлов \n"
                        "/add_watched - добавить в просмотренные \n"
                        "/add_will_see - добавить в желаемые \n"
                        "/delete_anime - удалить тайтл из желаемых \n")

# показывает список просмотренных тайтлов
@dp.message_handler(commands=["watched_list"]) #декоратор приёма команды
async def show_watched_list(message: types.Message):
    anime_file = open('list.txt', 'r', encoding="utf-8")
    anime_list = anime_file.read()
    await message.reply(anime_list)
    anime_file.close()

# показывает список запланированных тайтлов
@dp.message_handler(commands=["will_see"])
async def show_will_see(message: types.Message):
    anime_file = open('see.txt', 'r', encoding="utf-8")
    anime_list = anime_file.read()
    await message.reply(anime_list)
    anime_file.close()

# выдаёт рандомный тайтл из запланированных с возможностью попросить ещё
@dp.message_handler(commands=["random_anime"])
async def give_random_anime(message: types.Message):
    markup = InlineKeyboardMarkup() # хрень без которой не работают Inline кнопки
    btn_more = InlineKeyboardButton("Ещё", callback_data="btn_more") # добавление самой Inline кнопки
    anime_file = open('see.txt', 'r', encoding="utf-8")
    anime_text = anime_file.read()
    list_anime = anime_text.split('\n')
    random_anime = random.choice(list_anime) #выбор рандомного элемента в списке
    markup.add(btn_more) # прикрепление кнопок к соообщению?
    await message.reply(random_anime, reply_markup=markup)
    anime_file.close()


# эта самая кнопка ещё
@dp.callback_query_handler(lambda c: c.data == "btn_more") #реакцию на нажатие кнопки
async def btn_more_random(call: types.callback_query):
    markup = InlineKeyboardMarkup()
    btn_more = InlineKeyboardButton("Ещё", callback_data="btn_more")
    with open("see.txt", "r", encoding="utf-8") as anime_file:
        anime_text = anime_file.read()
        list_anime = anime_text.split('\n')
        random_anime = random.choice(list_anime)
    markup.add(btn_more)
    await bot.answer_callback_query(call.id) # хрень, чтобы кнопка долго не мигала?
    await bot.send_message(call.message.chat.id, random_anime, reply_markup=markup) #отправка сообщения


# показывает числа просмотренных тайтлов
@dp.message_handler(commands=["count_watched"])
async def count_watched_anime(message: types.Message):
    anime_file = open('list.txt', 'r', encoding="utf-8")
    anime_list = anime_file.read()
    anime_list = anime_list.split(";")
    await message.reply(len(anime_list) - 1)
    anime_file.close()


# показывает число запланированных тайтлов
@dp.message_handler(commands=["count_will_see"])
async def count_will_see_anime(message: types.Message):
    anime_file = open('see.txt', 'r', encoding="utf-8")
    anime_text = anime_file.read()
    list_anime = anime_text.split('\n')
    await message.reply(len(list_anime))
    anime_file.close()


# класс без которого вообще не будет работать машина состояний
class Add_in_list(StatesGroup): # набор состояний
    waiting_add_wached = State()
    waiting_add_will_see = State()
    waiting_delete_anime = State()


#задавание состояния ожидания добавления нового тайтла в просмотренные
@dp.message_handler(commands=["add_watched"])
async def state_add_watched(message: types.Message, state: FSMContext):
    await message.reply("Какое аниме я посмотрел?")
    await state.set_state(Add_in_list.waiting_add_wached.state) # задавание состояния ожидания сообщения


#добавление тайтла в просмотренные
@dp.message_handler(state=Add_in_list.waiting_add_wached) # реакция на изменения состояния
async def add_watched(message: types.Message, state: FSMContext):
    await state.update_data(new_anime=message.text, encoding="utf-8")
    new_anime = message.text + "; "
    with open('list.txt', 'a+', encoding="utf-8") as anime_file:
        anime_file.write(f'{new_anime}')
    await message.answer(f"Записано")
    await state.finish() # завершение состояния


#задавание состояния ожидания добавления нового тайтла в запланированные
@dp.message_handler(commands=["add_will_see"])
async def state_add_will_see(message: types.Message, state: FSMContext):
    await message.reply("Какое аниме добавить?")
    await state.set_state(Add_in_list.waiting_add_will_see)


#добавление тайтла в запланированные
@dp.message_handler(state=Add_in_list.waiting_add_will_see)
async def add_will_see(message: types.Message, state: FSMContext):
    await state.update_data(new_anime=message.text, encoding="utf-8")
    new_anime = message.text + "\n"
    with open('see.txt', 'a+', encoding="utf-8") as anime_file:
        anime_file.write(f'{new_anime}')
    await message.answer(f"Записано")
    await state.finish()


#задавание состояния ожидания удаления тайтла из запланированных
@dp.message_handler(commands=["delete_anime"])
async def state_remove_anime(message: types.Message, state: FSMContext):
    await message.reply("Что удаляем?")
    await state.set_state(Add_in_list.waiting_delete_anime)


# удаления тайтла из запланированных
@dp.message_handler(state=Add_in_list.waiting_delete_anime)
async def remove_anime(message: types.Message, state: FSMContext):
    flag = True
    await state.update_data(delete_anime=message.text, encoding="utf-8")
    delete_anime =message.text
    with open("see.txt", 'r', encoding="utf-8") as anime_file:
        anime_list= anime_file.read()
        anime_list=anime_list.split('\n')
        try:
            anime_list.remove(delete_anime)
        except:
            await message.reply("Такого нет, ты накосячил")
            flag = False
    with open("see.txt", "w", encoding="utf-8") as new_anime_file:
        anime_str= "\n".join(anime_list)
        new_anime_file.write(anime_str)
    if flag:
        await message.answer(f"Вроде как удалено")
    else:
        await message.answer(f"Нихера не удалено, пытайся ещё")
    await state.finish()

def BOT():
    executor.start_polling(dp)
