import json

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

from config import BUTTONS, REG_BUTTONS


def name_to_cmd(names):
    return ['/' + name for name in names]


def make_base_kbd(buttons_name, row_width=3):
    keyboard = ReplyKeyboardMarkup(row_width=row_width, resize_keyboard=True)
    buttons = [KeyboardButton(name) for name in buttons_name]
    return keyboard.add(*buttons)


def make_welcome_kbd(*args, **kwargs):
    row_width = 2
    buttons_name = name_to_cmd(
        [BUTTONS['all_races'],
         BUTTONS['btn_make_registr'],
         BUTTONS['cancel_this'],
         BUTTONS['cancel_all'], ]
        )
    return make_base_kbd(buttons_name, row_width)


def cancel_this_kbd(*args, **kwargs):
    buttons_name = name_to_cmd([
         BUTTONS['cancel_this']
        ])
    return make_base_kbd(buttons_name)


def pass_keyboard(obj):
    pass_button = InlineKeyboardButton(
        text=REG_BUTTONS['pass'],
        callback_data=json.dumps(
            {'name': 'pass', 'payload': None}))
    return InlineKeyboardMarkup().add(pass_button)


def category_keyboard(obj):
    categories = obj.race['race_categories']
    buttons = []
    for category in categories:
        text = category['name']
        callback_data = json.dumps(
            {'name': 'category',
             'race_id': obj.race['id'],
             'cat_id': category['id']}
        )
        button = InlineKeyboardButton(text=text, callback_data=callback_data)
        buttons.append(button)
    return InlineKeyboardMarkup(row_width=1).add(*buttons)


def make_inline_buttons_row(datas: list) -> list:
    buttons = []
    for item in datas:
        text = item[0]
        callback_data = json.dumps(item[1])
        button = InlineKeyboardButton(text=text, callback_data=callback_data)
        buttons.append(button)
    return buttons


def races_buttons(races: list, cur_page: int, pages: int = 1):
    datas = (
        (item['name'],
         {'name': 'race_data',
          'race_id': item['id']}) for item in races
    )
    buttons = make_inline_buttons_row(datas)
    if pages > 1 and cur_page < pages:
        calbac_data = json.dumps({'name': 'next'})
        next_btn = InlineKeyboardButton(
            text=BUTTONS['next'],
            callback_data=calbac_data)
        buttons.append(next_btn)
    return InlineKeyboardMarkup(row_width=1).add(*buttons)


def race_detail_button(obj):
    r = obj.race
    btn_race_detail = InlineKeyboardButton(
        text=REG_BUTTONS['race_detail'],
        callback_data=json.dumps(
            {'name': 'race_data',
             'race_id': r['id']})
        )
    return InlineKeyboardMarkup().add(btn_race_detail)


def reg_update_button(obj):
    reg_code = obj.id
    btn_reg_update = InlineKeyboardButton(
        text=REG_BUTTONS['reg_update'],
        callback_data=json.dumps(
            {'name': 'update',
             'reg_code': reg_code})
        )
    return InlineKeyboardMarkup().add(btn_reg_update)


def reg_start_button(race_id):
    btn_reg_update = InlineKeyboardButton(
        text=REG_BUTTONS['reg_start'],
        callback_data=json.dumps(
            {'name': 'reg_start',
             'race_id': race_id})
        )
    return InlineKeyboardMarkup().add(btn_reg_update)
