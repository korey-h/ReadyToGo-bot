import json
import logging
import os
import threading
import time
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv
from telebot import TeleBot

import static_buttons as sb
from api_handlers import get_races, race_detail_handler
from config import (
    ABOUT_RACE, ALLOWED_BUTTONS,
    BUTTONS, MESSAGES,
    PAGE_LIMIT, REG_MESSAGE)
from models import User


load_dotenv('.env')
with open('about.txt', encoding='utf-8') as f:
    ABOUT = f.read()

bot = TeleBot(os.getenv('TOKEN'))
users = {}

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


def try_exec_stack(message, user: User, data):
    command = user.get_cmd_stack()
    if command and callable(command['cmd']):
        context = {
            'message': message,
            'user': user,
            'data': data,
            'from': 'stack'}
        command['cmd'](**context)


@bot.message_handler(commands=['start'])
def welcome(message):
    user = get_user(message)
    if user.is_stack_empty():
        mess = MESSAGES['welcome']
        bot.send_message(user.id, mess, reply_markup=sb.make_welcome_kbd())


@bot.message_handler(commands=['подсказка', 'help'])
def about(message):
    user = get_user(message)
    bot.send_message(user.id, ABOUT)


def has_unfinished_commands(user: User, cmd_name: str):
    cmd = user.get_cmd_stack()
    if cmd and cmd['cmd_name'] != cmd_name:
        text = MESSAGES['no_finished_commands'] % (cmd.__doc__)
        bot.send_message(user.id, text=text)
        return True
    return False


def is_buttons_alowwed(func_name: str, button_data: dict, user: User):
    btn_name = button_data.get('name')
    allowed = ALLOWED_BUTTONS.get(func_name)
    if not btn_name or not allowed or btn_name not in allowed:
        text = MESSAGES['not_allowed_btn']
        bot.send_message(user.id, text=text)
        return False
    return True


@bot.message_handler(commands=[BUTTONS['all_races']])
def show_all_races(message, user: User = None, data=None, *args, **kwargs):
    '''Просмотр мероприятий с активной регистрацией'''

    self_name = 'show_all_races'
    user = user if user else get_user(message)
    called_from = kwargs.get('from')
    if has_unfinished_commands(user, self_name):
        return
    elif user.is_stack_empty():
        user.set_cmd_stack([self_name, show_all_races])
    elif not called_from:
        return bot.send_message(user.id, text=MESSAGES['cmd_always_on'])
    elif isinstance(data, dict):
        if not is_buttons_alowwed(self_name, data, user):
            return
    else:
        return

    keyboard = None
    up_stack = user.cmd_stack_pop()
    stack_data = up_stack['data']
    cur_page = stack_data.get('cur_page')
    cur_page = 1 if not cur_page else cur_page
    pages_am = stack_data.get('pages_am')
    if pages_am and data.get('name') == 'next':
        if cur_page < pages_am:
            cur_page += 1

    res = get_races(page=cur_page)
    if res['status'] == 200:
        page = res['data']
        races_list = page['results']
        pages_am = page['count'] // PAGE_LIMIT + 1
        if cur_page < pages_am:
            params = [
                self_name, show_all_races,
                {'message': message, 'user': user,
                 'cur_page': cur_page, 'pages_am': pages_am}
                ]
            user.set_cmd_stack(params)
        text = MESSAGES['mess_finded_races'].format(cur_page, pages_am)
        keyboard = sb.races_buttons(races_list, cur_page, pages_am)
    else:
        if res['status'] == 404:
            text = MESSAGES['not_found']
        elif res['status'] in range(500, 600):
            text = MESSAGES['conection_error']
        else:
            text = MESSAGES['unknown_error']
        user.set_cmd_stack(up_stack)
    bot.send_message(user.id, text=text, reply_markup=keyboard)


@bot.message_handler(commands=[BUTTONS['btn_make_registr']])
def registration(message, user: User = None, data=None, *args, **kwargs):
    '''Регистрация на мероприятие'''

    self_name = 'registration'
    user = user if user else get_user(message)
    called_from = kwargs.get('from')
    if not user.reg_proces:
        user.start_registration()
        user.set_cmd_stack((self_name, registration))
        if called_from and called_from == 'force_start':
            user.reg_proces.step += 1
    elif not called_from or called_from == 'force_start':
        race_name = user.reg_proces.race['name']
        return bot.send_message(
            user.id,
            text=REG_MESSAGE['reg_always_on'].format(race_name)
            )
    elif called_from == 'force_start':
        context = user.reg_proces.repeat_last_step()
        return bot.send_message(user.id, **context)

    if has_unfinished_commands(user, self_name):
        return
    if isinstance(data, dict):
        if not is_buttons_alowwed(self_name, data, user):
            return
        data = data['payload'] if 'payload' in data.keys() else data
    if data is None and user.reg_proces.step > 0:
        context = user.reg_proces.pass_step()
    else:
        context = user.reg_proces.exec(data)
    if not user.reg_proces.is_active:
        user.stop_registration()
        user.cmd_stack_pop()
    bot.send_message(user.id, **context)


def force_start(message, user: User, data: str):
    data = data['race_id']
    kwargs = {'from': 'force_start'}
    return registration(message, user, data, **kwargs)


@bot.message_handler(commands=[BUTTONS['btn_reg_update']])
def reg_update(message, user: User = None, data=None, *args, **kwargs):
    '''Редактирование заявки'''

    self_name = 'update_registration'
    user = user if user else get_user(message)
    called_from = kwargs.get('from')
    if not user.reg_proces:
        user.update_registration()
        user.set_cmd_stack((self_name, reg_update))
        if called_from and called_from == 'force_start':
            user.reg_proces.step += 1
    elif not called_from or called_from == 'force_start':
        race_name = user.reg_proces.race['name']
        return bot.send_message(
            user.id,
            text=REG_MESSAGE['reg_always_on'].format(race_name)
            )
    elif called_from == 'force_start':
        context = user.reg_proces.repeat_last_step()
        return bot.send_message(user.id, **context)

    if has_unfinished_commands(user, self_name):
        return
    if isinstance(data, dict):
        if not is_buttons_alowwed(self_name, data, user):
            return
        data = data['payload'] if 'payload' in data.keys() else data
        step = data['step']
        user.reg_proces.step = step
        if step == user.reg_proces._finish_step:
            context = user.reg_proces.make_registration()
        else:
            context = user.reg_proces.mess_wrapper(step)
    elif data is None and user.reg_proces.step > 0:
        context = user.reg_proces.pass_step()
    else:
        context = user.reg_proces.exec(data)
    if not user.reg_proces.is_active:
        user.stop_registration()
        user.cmd_stack_pop()
    bot.send_message(user.id, **context)


def about_race(message, user: User, data: str):
    if user.reg_proces:
        race = user.reg_proces.race
    else:
        race_id = data['race_id']
        detail = race_detail_handler(race_id)
        if detail['error']:
            return bot.send_message(
                user.id, text=detail['error'])
        else:
            race = detail['data']

    categories = '-'
    if race['race_categories']:
        cat_names = [cat['name'] for cat in race['race_categories']]
        categories = ', '.join(cat_names)
    cup = race['cup']['name'] if race['cup'] else ''
    params = [
        race['name'], race['date'], cup,
        race['town'], categories, race['description']
    ]
    return bot.send_message(
        user.id,
        text=ABOUT_RACE.format(*params),
        parse_mode='Markdown',
        reply_markup=sb.reg_start_button(race['id']))


@bot.message_handler(commands=[BUTTONS['cancel_all']])
def cancel_all(message):
    user = get_user(message)
    user.cancel_all()
    bot.send_message(
        user.id, MESSAGES['mess_cancel_all'],
        reply_markup=sb.make_welcome_kbd())


@bot.message_handler(commands=[BUTTONS['cancel_this']])
def cancel_this(message):
    user = get_user(message)
    up_stack = user.cmd_stack_pop()
    if not up_stack or not up_stack['cmd_name']:
        return
    cmd = up_stack['cmd']
    all_comm = [cmd.__doc__, ]
    while up_stack:
        cmd = up_stack['cmd']
        prev = user.get_cmd_stack()
        if not prev or cmd != prev['called_by']:
            break
        user.cmd_stack_pop()
        all_comm.append(prev['cmd'].__doc__)
    out = ', '.join(all_comm)
    bot.send_message(
        user.id,
        MESSAGES['mess_cancel_this'].format(out),
        reply_markup=sb.make_welcome_kbd())


@bot.message_handler(content_types=["text"])
def text_router(message):
    user = get_user(message)
    data = message.text
    try_exec_stack(message, user, data)


@bot.callback_query_handler(func=lambda call: True, )
def inline_keys_exec(call):
    message = call.message
    user = get_user(message)
    data = json.loads(call.data)
    btn_name = data.get('name')
    if btn_name == 'reg_start':
        return force_start(message, user, data)
    elif btn_name == 'race_data':
        return about_race(message, user, data)
    try_exec_stack(message, user, data)

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
    # develop_id = os.getenv('DEVELOP_ID')
    # t1 = threading.Thread(target=err_informer, args=[develop_id])
    # t1.start()
    bot.polling(non_stop=True)
    # while True:
    #     try:
    #         bot.polling(non_stop=True)
    #     except Exception as error:
    #         err_info = error.__repr__()
    #         logger.exception(error)