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

# класс без которого вообще не будет работать машина состояний
class Add_in_list(StatesGroup): # набор состояний
    waiting_add_wached = State()
    waiting_add_will_see = State()
    waiting_delete_anime = State()
    waiting_add_complete_game=State()
    waiting_add_will_play_game = State()
    waiting_delete_game = State()

@dp.message_handler(commands=['start'])  # что происходит при команде старт
async def begin(message: types.Message):
    markup = InlineKeyboardMarkup()
    btn_mode_game=InlineKeyboardButton("Игры", callback_data="mode_game")
    btn_mode_anime = InlineKeyboardButton("Аниме", callback_data="mode_anime")
    markup.add(btn_mode_game, btn_mode_anime)
    await bot.send_message(message.chat.id, "Какие команды показать?", reply_markup=markup)

#показывает список доступных команд для аниме
@dp.callback_query_handler(lambda c: c.data == "mode_anime")
async def show_comand_anime(call: types.callback_query):
    await bot.send_message(call.message.chat.id, "/watched_list - список просмотренных тайтлов \n"
                        "/will_see - список запланированных тайтлов \n"
                        "/random_anime - случайное аниме из запланированных \n"
                        "/count_watched - число просмотренных тайтлов \n"
                        "/count_will_see - число запланированных тайтлов \n"
                        "/add_watched - добавить в просмотренные \n"
                        "/add_will_see - добавить в желаемые \n"
                        "/delete_anime - удалить тайтл из желаемых \n")


#показывает список доспупных команд для игр
@dp.callback_query_handler(lambda c: c.data == "mode_game")
async def show_command_game(call: types.callback_query):
    await bot.send_message(call.message.chat.id, "/complete_list - список пройденных игр \n"
                                                 "/will_play - список запланированных игр \n"
                                                 "/random_game - рандомная игра из списка \n"
                                                 "/add_complete_game - добавить игру в пройденные \n"
                                                 "/add_will_play_game - добавить игру в запланированные \n"
                                                 "/delete_game - удалить игру из запланированных \n")


#выводит список пройденных игр
@dp.message_handler(commands=["complete_list"])
async def show_complete_game(message: types.Message):
    with open("Complete_list.txt", "r",encoding="utf-8") as file:
        game_list=file.read()
    await message.reply(game_list)


#выводит список запланированных игр
@dp.message_handler(commands=["will_play"])
async def show_will_play(message: types.Message):
    with open("Will_play.txt", "r",encoding="utf-8") as file:
        game_list=file.read()
    await message.reply(game_list)

#выдаёт рандомную игру из запланированных и есть кнопка "ещё"
@dp.message_handler(commands=["random_game"])
async def give_random_game(message: types.Message):
    markup = InlineKeyboardMarkup()
    btn_more_game = InlineKeyboardButton("Ещё", callback_data="btn_more_game")
    with open("Will_play.txt", "r",encoding="utf-8") as file:
        all_game=file.read()
        list_game = all_game.split("\n")
        random_game=random.choice(list_game)
    markup.add(btn_more_game)
    await message.reply(random_game, reply_markup=markup)


#кпопка "ещё" для игр
@dp.callback_query_handler(lambda c: c.data == "btn_more_game")
async def btn_more_random(call: types.callback_query):
    markup = InlineKeyboardMarkup()
    btn_more_game = InlineKeyboardButton("Ещё", callback_data="btn_more_game")
    with open("Will_play.txt", "r",encoding="utf-8") as file:
        all_game=file.read()
        list_game = all_game.split("\n")
        random_game=random.choice(list_game)
    markup.add(btn_more_game)
    await bot.answer_callback_query(call.id)
    await bot.send_message(call.message.chat.id, random_game, reply_markup=markup)


#задавание состояния ожидания пройденной игры
@dp.message_handler(commands=["add_complete_game"])
async def state_add_complete_game(message: types.Message, state: FSMContext):
    await message.reply("Какую игру я прошёл?")
    await state.set_state(Add_in_list.waiting_add_complete_game.state) # задавание состояния ожидания сообщения


#добаление текста следующего сообщения в список пройденных игр
@dp.message_handler(state=Add_in_list.waiting_add_complete_game) # реакция на изменения состояния
async def add_complete_game(message: types.Message, state: FSMContext):
    await state.update_data(new_game=message.text, encoding="utf-8")
    new_game = message.text + "\n"
    with open('Complete_list.txt', 'a+', encoding="utf-8") as file:
        file.write(f'{new_game}')
    await message.answer(f"Записано")
    await state.finish() # завершение состояния


#задание состояния удаления игры
@dp.message_handler(commands=["delete_game"])
async def state_delete_game(message: types.Message, state: FSMContext):
    await message.reply("Какую игру удалить из списка?")
    await state.set_state(Add_in_list.waiting_delete_game.state)


# удаления игры из запланированных
@dp.message_handler(state=Add_in_list.waiting_delete_game)
async def remove_game(message: types.Message, state: FSMContext):
    flag = True
    await state.update_data(delete_game=message.text, encoding="utf-8")
    delete_game =message.text
    with open("Will_play.txt", 'r', encoding="utf-8") as file:
        game_list= file.read()
        game_list= game_list.split('\n')
        try:
            game_list.remove(delete_game)
        except:
            await message.reply("Такого нет, ты накосячил")
            flag = False
    with open("Will_play.txt", "w", encoding="utf-8") as new_game_file:
        game_str= "\n".join(game_list)
        new_game_file.write(game_str)
    if flag:
        await message.answer(f"Вроде как удалено")
    else:
        await message.answer(f"Нихера не удалено, пытайся ещё")
    await state.finish()


#задавание состояния ожидания запланированной игры
@dp.message_handler(commands=["add_will_play_game"])
async def state_add_will_play_game(message: types.Message, state: FSMContext):
    await message.reply("Какую игру я хочу пройти?")
    await state.set_state(Add_in_list.waiting_add_will_play_game.state)


#добаление текста следующего сообщения в список запланированных игр
@dp.message_handler(state=Add_in_list.waiting_add_will_play_game) # реакция на изменения состояния
async def add_will_play_game(message: types.Message, state: FSMContext):
    await state.update_data(new_game=message.text, encoding="utf-8")
    new_game = message.text + "\n"
    with open('Will_play.txt', 'a+', encoding="utf-8") as file:
        file.write(f'{new_game}')
    await message.answer(f"Записано")
    await state.finish()


# показывает список просмотренных тайтлов
@dp.message_handler(commands=["watched_list"]) #декоратор приёма команды
async def show_watched_list(message: types.Message):
    anime_file = open('list_anime.txt', 'r', encoding="utf-8")
    anime_list = anime_file.read()
    await message.reply(anime_list)
    anime_file.close()


# показывает список запланированных тайтлов
@dp.message_handler(commands=["will_see"])
async def show_will_see(message: types.Message):
    anime_file = open('see_anime.txt', 'r', encoding="utf-8")
    anime_list = anime_file.read()
    await message.reply(anime_list)
    anime_file.close()



# выдаёт рандомный тайтл из запланированных с возможностью попросить ещё
@dp.message_handler(commands=["random_anime"])
async def give_random_anime(message: types.Message):
    markup = InlineKeyboardMarkup() # хрень без которой не работают Inline кнопки
    btn_more = InlineKeyboardButton("Ещё", callback_data="btn_more") # добавление самой Inline кнопки
    anime_file = open('see_anime.txt', 'r', encoding="utf-8")
    anime_text = anime_file.read()
    list_anime = anime_text.split('\n')
    random_anime = random.choice(list_anime) #выбор рандомного элемента в списке
    markup.add(btn_more) # прикрепление кнопок к соообщению?
    await message.reply(random_anime, reply_markup=markup)
    anime_file.close()


# эта самая кнопка ещё для аниме
@dp.callback_query_handler(lambda c: c.data == "btn_more") #реакцию на нажатие кнопки
async def btn_more_random(call: types.callback_query):
    markup = InlineKeyboardMarkup()
    btn_more = InlineKeyboardButton("Ещё", callback_data="btn_more")
    with open("see_anime.txt", "r", encoding="utf-8") as anime_file:
        anime_text = anime_file.read()
        list_anime = anime_text.split('\n')
        random_anime = random.choice(list_anime)
    markup.add(btn_more)
    await bot.answer_callback_query(call.id) # хрень, чтобы кнопка долго не мигала?
    await bot.send_message(call.message.chat.id, random_anime, reply_markup=markup) #отправка сообщения


# показывает числа просмотренных тайтлов
@dp.message_handler(commands=["count_watched"])
async def count_watched_anime(message: types.Message):
    anime_file = open('list_anime.txt', 'r', encoding="utf-8")
    anime_list = anime_file.read()
    anime_list = anime_list.split("\n")
    await message.reply(len(anime_list)-1)
    anime_file.close()


# показывает число запланированных тайтлов
@dp.message_handler(commands=["count_will_see"])
async def count_will_see_anime(message: types.Message):
    anime_file = open('see_anime.txt', 'r', encoding="utf-8")
    anime_text = anime_file.read()
    list_anime = anime_text.split('\n')
    await message.reply(len(list_anime)-1)
    anime_file.close()



#задавание состояния ожидания добавления нового тайтла в просмотренные
@dp.message_handler(commands=["add_watched"])
async def state_add_watched(message: types.Message, state: FSMContext):
    await message.reply("Какое аниме я посмотрел?")
    await state.set_state(Add_in_list.waiting_add_wached.state) # задавание состояния ожидания сообщения


#добавление тайтла в просмотренные
@dp.message_handler(state=Add_in_list.waiting_add_wached) # реакция на изменения состояния
async def add_watched(message: types.Message, state: FSMContext):
    await state.update_data(new_anime=message.text, encoding="utf-8")
    new_anime = message.text + "\n"
    with open('list_anime.txt', 'a+', encoding="utf-8") as anime_file:
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
    with open('see_anime.txt', 'a+', encoding="utf-8") as anime_file:
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
    with open("see_anime.txt", 'r', encoding="utf-8") as anime_file:
        anime_list= anime_file.read()
        anime_list=anime_list.split('\n')
        try:
            anime_list.remove(delete_anime)
        except:
            await message.reply("Такого нет, ты накосячил")
            flag = False
    with open("see_anime.txt", "w", encoding="utf-8") as new_anime_file:
        anime_str= "\n".join(anime_list)
        new_anime_file.write(anime_str)
    if flag:
        await message.answer(f"Вроде как удалено")
    else:
        await message.answer(f"Нихера не удалено, пытайся ещё")
    await state.finish()

def BOT():
    executor.start_polling(dp)
