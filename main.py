import telebot
import random
import pickle
from re import match
from math import atan, pi
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


def chance(n):
    return atan(n/12)/pi * 1.8


def comp_def(n):
    return atan(n/7)/pi * 1.9


def is_ok(text):
    mat = match("""^[а-яА-ЯёЁa-zA-Z0-9 _-]+$""", text)
    return bool(mat) and 3 <= len(text) <= 10


def get_name(message: telebot.types.Message):
    print(message.chat.id, "in get_name")
    try:
        info[message.chat.id]["user_info"]["name"] = message.text
        if not is_ok(message.text):
            info[message.chat.id]["user_info"]["name"] = ""
            raise ValueError
        for i in info:
            if info[i]["user_info"]["name"] == message.text:
                if i == message.chat.id:
                    continue
                info[message.chat.id]["user_info"]["name"] = ""
                raise IOError
        start_handler(message)
    except IOError:
        bot.send_message(chat_id=message.chat.id,
                         text="Имя уже занято, повторите попытку")
        bot.register_next_step_handler(message, get_name)
    except Exception as e:
        print(e)
        bot.send_message(chat_id=message.chat.id,
                         text="Введено некорректное имя, повторите попытку")
        bot.register_next_step_handler(message, get_name)


@bot.message_handler(commands=["test"])
def test_handler(message: telebot.types.Message):
    if message.chat.id == id_god:
        if message.chat.id not in info:
            bot.send_message(chat_id=message.chat.id, text="Создай персонажа")
            return 0
        info[message.chat.id]["user_info"]["lvl"] += 1
        info[message.chat.id]["level_up"] = 3
        level_handler(message)
    else:
        bot.send_message(chat_id=message.chat.id, text="Нет доступа")


@bot.message_handler(commands=["save"])
def save_handler(message: telebot.types.Message):
    if message.chat.id == id_god:
        try:
            with open('out.txt', 'wb') as out:
                pickle.dump(info, out)
            print(info)
            bot.send_message(chat_id=message.chat.id, text="Успешно")
        except Exception as e:
            print(e)
            bot.send_message(chat_id=message.chat.id, text=f"Не успешно, {e}")
    else:
        bot.send_message(chat_id=message.chat.id, text="Нет доступа")


@bot.message_handler(commands=["load"])
def load_handler(message: telebot.types.Message):
    global info
    if message.chat.id == id_god:
        try:
            with open('out.txt', 'rb') as inp:
                info = pickle.load(inp)
            print(info)
            bot.send_message(chat_id=message.chat.id, text="Успешно")
        except Exception as e:
            print(e)
            bot.send_message(chat_id=message.chat.id, text=f"Не успешно, {e}")
    else:
        bot.send_message(chat_id=message.chat.id, text="Нет доступа")


@bot.message_handler(commands=["rating"])
def rating_handler(message: telebot.types.Message):
    print(message.chat.id, "in rating")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["level_up"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Сначала распределите очки характеристик")
    elif info[message.chat.id]["in_battle"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Вы в бою")
    elif not info[message.chat.id]["in_home"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Сначала вернитесь домой")
    else:
        temp = sorted([info[user_id]["user_info"] for user_id in info],
                      key=lambda x: (x["lvl"], x["exp_now"]), reverse=True)
        print(temp)
        top = "\n".join([str(temp[i]["name"]) + ": " + str(temp[i]["lvl"]) for i in range(min(10, len(temp)))])
        bot.send_message(chat_id=message.chat.id,
                         text=f"""
Топ 10

{top}
                         """)


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
def pre_start_handler(message: telebot.types.Message):
    print(message.chat.id, "in pre_start")
    if message.chat.id not in info:
        info[message.chat.id] = {
            "user_info": {"name": "", "exp_now": 0, "exp_need": 10, "lvl": 0, "atk": 0, "def": 0, "hp_now": 10,
                          "hp_max": 10, "real_def": 0,
                          "crit": 0, "crit_chance": 0, "dodge": 0, "dodge_chance": 0, "constitution": 0},
            "enemy_info": {"name": "wolf", "lvl": 1, "atk": 1, "def": 0, "hp_now": 10, "hp_max": 10, "real_def": 0,
                           "crit": 0, "crit_chance": 0, "dodge": 0, "dodge_chance": 0, "constitution": 0},
            "enemy_found": False,
            "level_up": 3,
            "in_battle": False,
            "relax": False,
            "in_home": False
        }
        msg = bot.send_message(chat_id=message.chat.id,
                               text=f"""
Введите уникальное имя
Оно может содержать латиницу, кириллицу, цифры и знаки "-" и "_"
Длина от 3 до 10 символов
                                """, reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, get_name)
    else:
        start_handler(message)


def start_handler(message: telebot.types.Message):
    print(message.chat.id, "in start")
    if info[message.chat.id]["user_info"]["lvl"] == 0:
        info[message.chat.id]["user_info"]["lvl"] += 1
        bot.send_message(chat_id=message.chat.id,
                         text=f"""
"Поднять атаку", чтобы поднять урон от вашей атаки на 1
"Поднять защиту", чтобы увеличить процент поглощения урона от вражеской атаки
"Поднять телосложение", чтобы увеличить ваше здоровье на 10
"Поднять критический удар", чтобы с большим шансом нанести в 2 раза больше урона
"Поднять уклонение", чтобы с большим шансом уклониться от вражеской атаки
                         """)
        level_handler(message)
    elif info[message.chat.id]["level_up"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Сначала распределите очки характеристик")
    elif info[message.chat.id]["in_battle"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Вы в бою")
    else:
        info[message.chat.id]["in_home"] = True
        if info[message.chat.id]["user_info"]["hp_now"] == info[message.chat.id]["user_info"]["hp_max"]:
            markup = create_keyboard(["Охота", "Характеристики", "Рейтинг"])
        else:
            markup = create_keyboard(["Охота", "Характеристики", "Отдых", "Рейтинг"])
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
    bot.send_message(chat_id=message.chat.id,
                     text=f"""
Имя: {info[message.chat.id]["user_info"]["name"]}
Уровень: {info[message.chat.id]["user_info"]["lvl"]}

Опыт: {info[message.chat.id]["user_info"]["exp_now"]}/{info[message.chat.id]["user_info"]["exp_need"]}
Очки здоровья: {info[message.chat.id]["user_info"]["hp_now"]}/{info[message.chat.id]["user_info"]["hp_max"]}

Атака: {info[message.chat.id]["user_info"]["atk"]}
Защита: {info[message.chat.id]["user_info"]["def"]}
Телосложение: {info[message.chat.id]["user_info"]["constitution"]}
Критический удар: {info[message.chat.id]["user_info"]["crit"]}
Уклонение: {info[message.chat.id]["user_info"]["dodge"]}
                     """)


@bot.message_handler(commands=["search"])
def search_handler(message: telebot.types.Message):
    print(message.chat.id, "in search")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["level_up"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Сначала распределите очки характеристик")
    elif info[message.chat.id]["in_battle"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Вы в бою")
    elif random.random() <= 0.4:
        info[message.chat.id]["enemy_found"] = False
        if info[message.chat.id]["user_info"]["hp_now"] == info[message.chat.id]["user_info"]["hp_max"]:
            markup = create_keyboard(["Искать дальше", "Характеристики", "В начало"])
        else:
            markup = create_keyboard(["Искать дальше", "Характеристики", "Отдых", "В начало"])
        bot.send_message(chat_id=message.chat.id, text="Вы не нашли врага", reply_markup=markup)
    else:
        if info[message.chat.id]["user_info"]["hp_now"] == info[message.chat.id]["user_info"]["hp_max"]:
            markup = create_keyboard(["Атака", "Искать дальше", "Характеристики", "В начало"])
        else:
            markup = create_keyboard(["Атака", "Искать дальше", "Характеристики", "Отдых", "В начало"])
        info[message.chat.id]["enemy_found"] = True
        enemy = random.randrange(0, 3)
        info[message.chat.id]["enemy_info"]["name"] = enemies[enemy]
        if info[message.chat.id]["user_info"]["lvl"] == 1:
            info[message.chat.id]["enemy_info"]["lvl"] = random.randrange(info[message.chat.id]["user_info"]["lvl"],
                                                                          info[message.chat.id]["user_info"]["lvl"] + 2)
        else:
            info[message.chat.id]["enemy_info"]["lvl"] = random.randrange(info[message.chat.id]["user_info"]["lvl"] - 1,
                                                                          info[message.chat.id]["user_info"]["lvl"] + 2)

        info[message.chat.id]["enemy_info"]["def"] = 0
        info[message.chat.id]["enemy_info"]["atk"] = 0
        info[message.chat.id]["enemy_info"]["constitution"] = 0
        info[message.chat.id]["enemy_info"]["crit"] = 0
        info[message.chat.id]["enemy_info"]["dodge"] = 0

        rand_list = ["atk", "def", "constitution", "crit", "dodge"]
        if enemy == 0:
            rand_list.extend(["atk", "atk", "constitution", "crit"])
        elif enemy == 1:
            rand_list.extend(["crit", "crit", "atk", "atk", "dodge"])
        elif enemy == 2:
            rand_list.extend(["atk", "atk", "def", "constitution", "constitution"])

        j = 0
        for i in range(info[message.chat.id]["enemy_info"]["lvl"]):
            if j == 5:
                j = 0
            info[message.chat.id]["enemy_info"][rand_list[j]] += 1
            j += 1
        for i in range(info[message.chat.id]["enemy_info"]["lvl"] * 2):
            info[message.chat.id]["enemy_info"][random.choice(rand_list)] += 1

        info[message.chat.id]["enemy_info"]["real_def"] = comp_def(info[message.chat.id]["enemy_info"]["def"])
        info[message.chat.id]["enemy_info"]["hp_max"] = info[message.chat.id]["enemy_info"]["constitution"] * 10 + 10
        info[message.chat.id]["enemy_info"]["dodge_chance"] = chance(info[message.chat.id]["enemy_info"]["dodge"])
        info[message.chat.id]["enemy_info"]["crit_chance"] = chance(info[message.chat.id]["enemy_info"]["crit"])
        info[message.chat.id]["enemy_info"]["hp_now"] = info[message.chat.id]["enemy_info"]["hp_max"]
        bot.send_message(chat_id=message.chat.id,
                         text=f"""
Вы нашли врага

Имя: {info[message.chat.id]["enemy_info"]["name"]}
Уровень: {info[message.chat.id]["enemy_info"]["lvl"]}

Очки здоровья: {info[message.chat.id]["enemy_info"]["hp_now"]}/{info[message.chat.id]["enemy_info"]["hp_max"]}

Атака: {info[message.chat.id]["enemy_info"]["atk"]}
Защита: {info[message.chat.id]["enemy_info"]["def"]}
Телосложение: {info[message.chat.id]["enemy_info"]["constitution"]}
Критический удар: {info[message.chat.id]["enemy_info"]["crit"]}
Уклонение: {info[message.chat.id]["enemy_info"]["dodge"]}
                         """, reply_markup=markup)
    info[message.chat.id]["in_home"] = False


@bot.message_handler(commands=["attack"])
def attack_handler(message: telebot.types.Message):
    print(message.chat.id, "in attack")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["level_up"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Сначала распределите очки характеристик")
    elif info[message.chat.id]["enemy_found"]:
        info[message.chat.id]["in_battle"] = True
        if random.random() <= info[message.chat.id]["enemy_info"]["dodge_chance"]:
            dmg_to_enemy = 0
            bot.send_message(chat_id=message.chat.id, text="Вы промахнулись")
        else:
            dmg_to_enemy = int(
                info[message.chat.id]["user_info"]["atk"] * (1 - info[message.chat.id]["enemy_info"]["real_def"]))
            if random.random() <= info[message.chat.id]["user_info"]["crit_chance"]:
                dmg_to_enemy *= 2
                bot.send_message(chat_id=message.chat.id, text="Вы нанесли критический удар")
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
Вы получили {info[message.chat.id]["enemy_info"]["lvl"]} ед. опыта
                             """)
            info[message.chat.id]["user_info"]["exp_now"] += info[message.chat.id]["enemy_info"]["lvl"]
            if info[message.chat.id]["user_info"]["exp_now"] >= info[message.chat.id]["user_info"]["exp_need"]:
                info[message.chat.id]["level_up"] = 3
                info[message.chat.id]["user_info"]["lvl"] += 1
                info[message.chat.id]["user_info"]["exp_now"] -= info[message.chat.id]["user_info"]["exp_need"]
                info[message.chat.id]["user_info"]["exp_need"] = info[message.chat.id]["user_info"]["lvl"] * 10
                bot.send_message(chat_id=message.chat.id,
                                 text=f"""
Поздравляем, вы получили новый уровень

"Поднять атаку", чтобы поднять урон от вашей атаки на 1
"Поднять защиту", чтобы увеличить процент поглощения урона от вражеской атаки
"Поднять телосложение", чтобы увеличить ваше здоровье на 10
"Поднять критический удар", чтобы с большим шансом нанести в 2 раза больше урона
"Поднять уклонение", чтобы с большим шансом уклониться от вражеской атаки
                                 """)
                level_handler(message)
            else:
                info_handler(message)
                start_handler(message)
        else:
            if random.random() <= info[message.chat.id]["user_info"]["dodge_chance"]:
                dmg_to_user = 0
                bot.send_message(chat_id=message.chat.id, text="Противник промахнулся")
            else:
                dmg_to_user = int(
                    info[message.chat.id]["enemy_info"]["atk"] * (1 - info[message.chat.id]["user_info"]["real_def"]))
                if random.random() <= info[message.chat.id]["enemy_info"]["crit_chance"]:
                    dmg_to_user *= 2
                    bot.send_message(chat_id=message.chat.id, text="Противник нанес критический удар")
            info[message.chat.id]["user_info"]["hp_now"] -= dmg_to_user
            if info[message.chat.id]["user_info"]["hp_now"] > 0:
                markup = create_keyboard(["Атака", "Побег"])
                bot.send_message(chat_id=message.chat.id,
                                 text=f"""
Вам нанесли {dmg_to_user} ед. урона

Вы: {info[message.chat.id]["user_info"]["hp_now"]}/{info[message.chat.id]["user_info"]["hp_max"]}
                                 """, reply_markup=markup)
            else:
                markup = create_keyboard(["В начало"])
                bot.send_message(chat_id=message.chat.id,
                                 text=f"""
Вам нанесли {dmg_to_user} ед. урона

Вы: {info[message.chat.id]["user_info"]["hp_now"]}/{info[message.chat.id]["user_info"]["hp_max"]}

Вы умерли, ваши данные удалены
                                 """, reply_markup=markup)
                del (info[message.chat.id])
    else:
        bot.send_message(chat_id=message.chat.id, text="Добыча не найдена")


@bot.message_handler(commands=["level_up"])
def level_handler(message: telebot.types.Message):
    print(message.chat.id, "in level")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["level_up"]:
        info[message.chat.id]["user_info"]["hp_now"] = info[message.chat.id]["user_info"]["hp_max"]
        info_handler(message)
        markup = create_keyboard(["Поднять атаку", "Поднять защиту", "Поднять телосложение",
                                  "Поднять критический удар", "Поднять уклонение"])
        bot.send_message(chat_id=message.chat.id,
                         text=f"""
Осталось распределить {info[message.chat.id]["level_up"]} ед. характеристик
                         """, reply_markup=markup)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Возвращайтесь, когда поднимете уровень")
        if not info[message.chat.id]["in_battle"]:
            info_handler(message)
            start_handler(message)


@bot.message_handler(commands=["point_to_attack"])
def plus_attack_handler(message: telebot.types.Message):
    print(message.chat.id, "in lvlup +att")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["level_up"]:
        info[message.chat.id]["level_up"] -= 1
        info[message.chat.id]["user_info"]["atk"] += 1
        level_handler(message)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Возвращайтесь, когда поднимите уровень")


@bot.message_handler(commands=["point_to_defence"])
def plus_defence_handler(message: telebot.types.Message):
    print(message.chat.id, "in lvlup +def")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["level_up"]:
        info[message.chat.id]["level_up"] -= 1
        info[message.chat.id]["user_info"]["def"] += 1
        info[message.chat.id]["user_info"]["real_def"] = comp_def(info[message.chat.id]["user_info"]["def"])
        level_handler(message)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Возвращайтесь, когда поднимите уровень")


@bot.message_handler(commands=["point_to_constitution"])
def plus_constitution_handler(message: telebot.types.Message):
    print(message.chat.id, "in lvlup +con")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["level_up"]:
        info[message.chat.id]["level_up"] -= 1
        info[message.chat.id]["user_info"]["constitution"] += 1
        info[message.chat.id]["user_info"]["hp_max"] += 10
        info[message.chat.id]["user_info"]["hp_now"] = info[message.chat.id]["user_info"]["hp_max"]
        level_handler(message)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Возвращайтесь, когда поднимите уровень")


@bot.message_handler(commands=["point_to_crit"])
def plus_crit_handler(message: telebot.types.Message):
    print(message.chat.id, "in lvlup +crit")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["level_up"]:
        info[message.chat.id]["level_up"] -= 1
        info[message.chat.id]["user_info"]["crit"] += 1
        info[message.chat.id]["user_info"]["crit_chance"] = chance(info[message.chat.id]["user_info"]["crit"])
        level_handler(message)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Возвращайтесь, когда поднимите уровень")


@bot.message_handler(commands=["point_to_dodge"])
def plus_dodge_handler(message: telebot.types.Message):
    print(message.chat.id, "in lvlup +dodge")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["level_up"]:
        info[message.chat.id]["level_up"] -= 1
        info[message.chat.id]["user_info"]["dodge"] += 1
        info[message.chat.id]["user_info"]["dodge_chance"] = chance(info[message.chat.id]["user_info"]["dodge"])
        level_handler(message)
    else:
        bot.send_message(chat_id=message.chat.id,
                         text="Возвращайтесь, когда поднимите уровень")


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
    else:
        bot.send_message(chat_id=message.chat.id, text="Вы не в бою, вам неоткуда сбегать")


@bot.message_handler(commands=["relax"])
def relax_handler(message: telebot.types.Message):
    print(message.chat.id, "in relax")
    if message.chat.id not in info:
        help_handler(message)
        return 0
    if info[message.chat.id]["level_up"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Сначала распределите очки характеристик")
    elif info[message.chat.id]["in_battle"]:
        bot.send_message(chat_id=message.chat.id,
                         text="Вы в бою")
    else:
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
    elif message.text == "В начало":
        pre_start_handler(message)
    elif message.text == "Рейтинг":
        rating_handler(message)
    elif message.text == "Поднять атаку":
        plus_attack_handler(message)
    elif message.text == "Поднять защиту":
        plus_defence_handler(message)
    elif message.text == "Поднять телосложение":
        plus_constitution_handler(message)
    elif message.text == "Поднять критический удар":
        plus_crit_handler(message)
    elif message.text == "Поднять уклонение":
        plus_dodge_handler(message)
    else:
        help_handler(message)


@bot.message_handler(content_types=telebot.util.content_type_media)
def wrong_message_handler(message: telebot.types.Message):
    print(message.chat.id, "in wrong")
    help_handler(message)


if __name__ == "__main__":
    bot.infinity_polling()
