import telebot
import random
import pickle
from bot_info import bot_token, id_god

enemies = ["Волк", "Лиса", "Медведь"]
info = {}
bot = telebot.TeleBot(token=bot_token)


def create_keyboard(list_names):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in list_names:
        item = telebot.types.KeyboardButton(name)
        markup.add(item)
    return markup


@bot.message_handler(commands=["save"])
def save_handler(message: telebot.types.Message):
    if message.chat.id == id_god:
        try:
            with open('out.txt', 'wb') as out:
                pickle.dump(info, out)
            print(info)
            bot.send_message(chat_id=message.chat.id, text="Успешно")
        except Exception:
            bot.send_message(chat_id=message.chat.id, text="Не успешно")
    else:
        bot.send_message(chat_id=message.chat.id, text="Нет доступа")


@bot.message_handler(commands=["load"])
def save_handler(message: telebot.types.Message):
    global info
    if message.chat.id == id_god:
        try:
            with open('out.txt', 'rb') as inp:
                info = pickle.load(inp)
            print(info)
            bot.send_message(chat_id=message.chat.id, text="Успешно")
        except Exception:
            bot.send_message(chat_id=message.chat.id, text="Не успешно")
    else:
        bot.send_message(chat_id=message.chat.id, text="Нет доступа")


@bot.message_handler(commands=["help"])
def help_handler(message: telebot.types.Message):
    print(message.chat.id, "in help")
    if message.chat.id not in info:
        markup = create_keyboard(["В начало"])
        bot.send_message(chat_id=message.chat.id,
                         text="""
Вы охотитесь на диких зверей
Выслеживайте их и убивайте, чтобы поднимать уровень и прокачиваться
Нажмите "Охота", чтобы начать выслеживать добычу
Когда добыча найдена, можете атаковать ее кнопкой "Атака" либо
найти другую добычу кнопкой "Искать дальше"
Следите за здоровьем, иногда следует отдохнуть, нажав "Отдых"
Если понимаете, что добыча вам не по силам, следует нажать "Побег"
Если хотите узнать свои характеристики - просто нажмите "Характеристики"
                         """, reply_markup=markup)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="""
Вы охотитесь на диких зверей
Выслеживайте их и убивайте, чтобы поднимать уровень и прокачиваться
Нажмите "Охота", чтобы начать выслеживать добычу
Когда добыча найдена, можете атаковать ее кнопкой "Атака" либо
найти другую добычу кнопкой "Искать дальше"
Следите за здоровьем, иногда следует отдохнуть, нажав "Отдых"
Если понимаете, что добыча вам не по силам, следует нажать "Побег"
Если хотите узнать свои характеристики - просто нажмите "Характеристики"
                         """)


@bot.message_handler(commands=["start"])
def start_handler(message: telebot.types.Message):
    print(message.chat.id, "in start")
    if message.chat.id not in info:
        info[message.chat.id] = {
            "user_info": {"exp_now": 0, "exp_need": 10, "lvl": 1, "atk": 2, "def": 0, "hp_now": 10, "hp_max": 10},
            "enemy_info": {"name": "wolf", "lvl": 1, "atk": 1, "def": 0, "hp_now": 10, "hp_max": 10},
            "enemy_found": False,
            "lewelup": False,
            "in_battle": False,
            "relax": False
        }
    if info[message.chat.id]["lewelup"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Сначала распределите очко навыков")
    elif info[message.chat.id]["in_battle"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Вы в бою")
    else:
        if info[message.chat.id]["user_info"]["hp_now"] == info[message.chat.id]["user_info"]["hp_max"]:
            markup = create_keyboard(["Охота", "Характеристики"])
        else:
            markup = create_keyboard(["Охота", "Характеристики", "Отдых"])
        if not info[message.chat.id]["relax"]:
            bot.send_message(chat_id=message.chat.id, text="Вы дома", reply_markup=markup)
        else:
            bot.send_message(chat_id=message.chat.id,
                             text=f"""
Вы отлежались и успешно восстановили здоровье
Очки здоровья - {info[message.chat.id]["user_info"]["hp_now"]}/{info[message.chat.id]["user_info"]["hp_max"]}
                             """, reply_markup=markup)


@bot.message_handler(commands=["info"])
def info_handler(message: telebot.types.Message):
    print(message.chat.id, "in info")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["lewelup"]:
        markup = create_keyboard(["Поднять атаку", "Поднять защиту и здоровье"])
        bot.send_message(chat_id=message.chat.id,
                         text=f"""
Уровень: {info[message.chat.id]["user_info"]["lvl"]}
Опыт: {info[message.chat.id]["user_info"]["exp_now"]}/{info[message.chat.id]["user_info"]["exp_need"]}
Очки здоровья: {info[message.chat.id]["user_info"]["hp_now"]}/{info[message.chat.id]["user_info"]["hp_max"]}
Атака: {info[message.chat.id]["user_info"]["atk"]}
Защита: {info[message.chat.id]["user_info"]["def"]}
                         """, reply_markup=markup)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text=f"""
Уровень: {info[message.chat.id]["user_info"]["lvl"]}
Опыт: {info[message.chat.id]["user_info"]["exp_now"]}/{info[message.chat.id]["user_info"]["exp_need"]}
Очки здоровья: {info[message.chat.id]["user_info"]["hp_now"]}/{info[message.chat.id]["user_info"]["hp_max"]}
Атака: {info[message.chat.id]["user_info"]["atk"]}
Защита: {info[message.chat.id]["user_info"]["def"]}
                         """)


@bot.message_handler(commands=["search"])
def search_handler(message: telebot.types.Message):
    print(message.chat.id, "in search")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["lewelup"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Сначала распределите очко навыков")
    elif info[message.chat.id]["in_battle"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Вы в бою")
    elif random.randrange(1, 10) > 5:
        info[message.chat.id]["enemy_found"] = False
        if info[message.chat.id]["user_info"]["hp_now"] == info[message.chat.id]["user_info"]["hp_max"]:
            markup = create_keyboard(["Искать дальше", "Характеристики", "В начало"])
        else:
            markup = create_keyboard(["Искать дальше", "Характеристики", "Отдых", "В начало"])
        bot.send_message(chat_id=message.chat.id,
                         text="Вы не нашли врага", reply_markup=markup)
    else:
        if info[message.chat.id]["user_info"]["hp_now"] == info[message.chat.id]["user_info"]["hp_max"]:
            markup = create_keyboard(["Атака", "Искать дальше", "Характеристики", "В начало"])
        else:
            markup = create_keyboard(["Атака", "Искать дальше", "Характеристики", "Отдых", "В начало"])
        info[message.chat.id]["enemy_found"] = True
        info[message.chat.id]["enemy_info"]["name"] = enemies[random.randrange(0, 3)]
        info[message.chat.id]["enemy_info"]["lvl"] = random.randrange(info[message.chat.id]["user_info"]["lvl"],
                                                                      info[message.chat.id]["user_info"]["lvl"] + 3)
        info[message.chat.id]["enemy_info"]["def"] = random.randrange(0, info[message.chat.id]["enemy_info"]["lvl"])
        info[message.chat.id]["enemy_info"]["atk"] = info[message.chat.id]["enemy_info"]["lvl"] - \
                                                     info[message.chat.id]["enemy_info"]["def"]
        info[message.chat.id]["enemy_info"]["hp_max"] = info[message.chat.id]["enemy_info"]["def"] * 10 + 10
        info[message.chat.id]["enemy_info"]["hp_now"] = info[message.chat.id]["enemy_info"]["hp_max"]
        bot.send_message(chat_id=message.chat.id,
                         text=f"""
Вы нашли врага
Имя: {info[message.chat.id]["enemy_info"]["name"]}
Уровень: {info[message.chat.id]["enemy_info"]["lvl"]}
Очки здоровья: {info[message.chat.id]["enemy_info"]["hp_now"]}/{info[message.chat.id]["enemy_info"]["hp_max"]}
Атака: {info[message.chat.id]["enemy_info"]["atk"]}
Защита: {info[message.chat.id]["enemy_info"]["def"]}
                         """, reply_markup=markup)


@bot.message_handler(commands=["attack"])
def attack_handler(message: telebot.types.Message):
    print(message.chat.id, "in attack")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["enemy_found"]:
        markup = create_keyboard(["Атака", "Побег"])
        info[message.chat.id]["in_battle"] = True
        dmg_to_enemy = max(info[message.chat.id]["user_info"]["atk"] - info[message.chat.id]["enemy_info"]["def"], 0)
        info[message.chat.id]["enemy_info"]["hp_now"] -= dmg_to_enemy
        bot.send_message(chat_id=message.chat.id,
                         text=f"""
Вы нанесли {dmg_to_enemy} ед. урона

{info[message.chat.id]["enemy_info"]["name"]}: {info[message.chat.id]["enemy_info"]["hp_now"]}/\
{info[message.chat.id]["enemy_info"]["hp_max"]}
                         """)
        if info[message.chat.id]["enemy_info"]["hp_now"] <= 0:
            info[message.chat.id]["enemy_found"] = False
            info[message.chat.id]["in_battle"] = False
            bot.send_message(chat_id=message.chat.id,
                             text=f"""
Поздравляем, вы победили врага
Получено {info[message.chat.id]["enemy_info"]["lvl"]} ед. опыта
                             """)
            info[message.chat.id]["user_info"]["exp_now"] += info[message.chat.id]["enemy_info"]["lvl"]
            if info[message.chat.id]["user_info"]["exp_now"] >= info[message.chat.id]["user_info"]["exp_need"]:
                info[message.chat.id]["lewelup"] = True
                info[message.chat.id]["user_info"]["lvl"] += 1
                info[message.chat.id]["user_info"]["exp_now"] = 0
                info[message.chat.id]["user_info"]["exp_need"] = info[message.chat.id]["user_info"]["lvl"] * 10
                bot.send_message(chat_id=message.chat.id,
                                 text=f"""
Поздравляем, вы получили новый уровень

"Поднять атаку", чтобы поднять атаку на 1
"Поднять защиту и здоровье", чтобы поднять защиту на 1 и здоровье на 10
                                 """)
                info_handler(message)
            else:
                info_handler(message)
                start_handler(message)
        else:
            dmg_to_user = max(info[message.chat.id]["enemy_info"]["atk"] - info[message.chat.id]["user_info"]["def"], 0)
            info[message.chat.id]["user_info"]["hp_now"] -= dmg_to_user
            if info[message.chat.id]["user_info"]["hp_now"] > 0:
                markup = create_keyboard(["Атака", "Побег"])
                bot.send_message(chat_id=message.chat.id,
                                 text=f"""
Вам нанесли {dmg_to_user} ед. урона

Вы: {info[message.chat.id]["user_info"]["hp_now"]}/{info[message.chat.id]["user_info"]["hp_max"]}
                                 """, reply_markup=markup)
            else:
                markup = create_keyboard(["Начать сначала"])
                bot.send_message(chat_id=message.chat.id,
                                 text=f"""
Вам нанесли {dmg_to_user} ед. урона

Вы: {info[message.chat.id]["user_info"]["hp_now"]}/{info[message.chat.id]["user_info"]["hp_max"]}

Вы умерли, ваши данные удалены
                                 """, reply_markup=markup)
                del (info[message.chat.id])
    else:
        bot.send_message(chat_id=message.chat.id, text="Добыча не найдена")


@bot.message_handler(commands=["point_to_attack"])
def plus_attack_handler(message: telebot.types.Message):
    print(message.chat.id, "in lwlup +a")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["lewelup"]:
        info[message.chat.id]["lewelup"] = False
        info[message.chat.id]["user_info"]["atk"] += 1
        info_handler(message)
        start_handler(message)


@bot.message_handler(commands=["point_to_defence"])
def plus_defence_handler(message: telebot.types.Message):
    print(message.chat.id, "in lwlup +d")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["lewelup"]:
        info[message.chat.id]["lewelup"] = False
        info[message.chat.id]["user_info"]["def"] += 1
        info[message.chat.id]["user_info"]["hp_max"] += 10
        info_handler(message)
        start_handler(message)


@bot.message_handler(commands=["escape"])
def escape_handler(message: telebot.types.Message):
    print(message.chat.id, "in escape")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["in_battle"]:
        info[message.chat.id]["in_battle"] = False
        bot.send_message(chat_id=message.chat.id,
                         text=f"""
Вы успешно сбежали из боя
Очки здоровья - {info[message.chat.id]["user_info"]["hp_now"]}/{info[message.chat.id]["user_info"]["hp_max"]}
                         """)
        start_handler(message)


@bot.message_handler(commands=["relax"])
def relax_handler(message: telebot.types.Message):
    print(message.chat.id, "in relax")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if not info[message.chat.id]["in_battle"] and not info[message.chat.id]["lewelup"]:
        info[message.chat.id]["user_info"]["hp_now"] = info[message.chat.id]["user_info"]["hp_max"]
        info[message.chat.id]["relax"] = True
        start_handler(message)
        info[message.chat.id]["relax"] = False


@bot.message_handler(content_types=["text"])
def text_message_handler(message: telebot.types.Message):
    print(message.chat.id, "написал", message.text)
    if message.text == "Охота" or message.text == "Искать дальше":
        search_handler(message)
    elif message.text == "Атака":
        attack_handler(message)
    elif message.text == "Характеристики":
        info_handler(message)
    elif message.text == "Отдых":
        relax_handler(message)
    elif message.text == "Побег":
        escape_handler(message)
    elif message.text == "В начало" or message.text == "Начать сначала":
        start_handler(message)
    elif message.text == "Поднять атаку":
        plus_attack_handler(message)
    elif message.text == "Поднять защиту и здоровье":
        plus_defence_handler(message)
    else:
        help_handler(message)


@bot.message_handler(content_types=telebot.util.content_type_media)
def wrong_message_handler(message: telebot.types.Message):
    print(message.chat.id, "in wrong")
    help_handler(message)


if __name__ == "__main__":
    bot.infinity_polling()
