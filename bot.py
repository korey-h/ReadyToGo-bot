import logging
import os
import threading
import time
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from telebot import TeleBot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

from .config import BUTTONS, MESSAGES
from .models import User

load_dotenv('.env')
with open('about.txt', encoding='utf-8') as f:
    ABOUT = f.read()

bot = TeleBot(os.getenv('TOKEN'))
users = {}
BREATH_TIME = 180

logger = logging.getLogger(__name__)
handler = RotatingFileHandler(
    'exceptions.log', maxBytes=50000000, backupCount=3)
logger.addHandler(handler)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

err_info = ''


def get_user(message) -> User:
    user_id = message.chat.id
    return users.setdefault(user_id, User(id=user_id))


def name_to_cmd(names):
    return ['/' + name for name in names]


def make_base_kbd(buttons_name):
    keyboard = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = [KeyboardButton(name) for name in buttons_name]
    return keyboard.add(*buttons)


@bot.message_handler(commands=['start'])
def welcome(message):
    user = get_user(message)
    if not user.training_active:
        buttons_name = name_to_cmd([BUTTONS['btn_make_registr']])
        keyboard = make_base_kbd(buttons_name)
        mess = MESSAGES['welcome']
        bot.send_message(user.id, mess, reply_markup=keyboard, )


@bot.message_handler(commands=['подсказка', 'help'])
def about(message):
    user = get_user(message)
    bot.send_message(user.id, ABOUT)


@bot.message_handler(commands=[BUTTONS['btn_make_registr']])
def registration(message, *args, **kwargs):
    '''Регистрация на мероприятие'''

    self_name = 'registration'
    user = get_user(message)
    cmd = user.get_cmd_stack()
    if cmd and cmd['name'] != self_name:
        text = MESSAGES['no_finished_commands'] % (cmd.__doc__)
        bot.send_message(user.id, text=text)

    data = kwargs['data']
    if not user.reg_proces:
        user.start_registration()
        user.set_cmd_stack((self_name, registration))
    context = user.reg_proces.exec(data)
    if not user.reg_proces.is_active:
        user.stop_registration()
    bot.send_message(user.id, **context)


@bot.message_handler(content_types=["text"])
def auditor(message):
    user = get_user(message)
    bot.send_message(user.id, '??')

##################################################################


def err_informer(chat_id):
    global err_info
    prev_err = err_info
    while True:
        if err_info == '' or err_info == prev_err:
            time.sleep(60)
            continue
        prev_err = err_info
        try:
            bot.send_message(
                chat_id,
                f'Было выброшено исключение: {err_info}')
        except Exception:
            pass


if __name__ == '__main__':
    develop_id = os.getenv('DEVELOP_ID')
    t1 = threading.Thread(target=err_informer, args=[develop_id])
    t1.start()

    while True:
        try:
            bot.polling(non_stop=True)
        except Exception as error:
            err_info = error.__repr__()
            logger.exception(error)
