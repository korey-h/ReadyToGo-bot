import json

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import REG_BUTTONS


def pass_keyboard(obj):
    pass_button = InlineKeyboardButton(
        text=REG_BUTTONS['pass'],
        callback_data='pass')
    return InlineKeyboardMarkup().add(pass_button)


def category_keyboard(obj):
    categories = obj.race['categories']
    buttons = []
    for category in categories:
        text = category['name']
        callback_data = json.dumps(
            {'race_id': obj.race['id'],
             'category_id': category['id']}
        )
        button = InlineKeyboardButton(text=text, callback_data=callback_data)
        buttons.append(button)
    return InlineKeyboardMarkup(row_width=1).add(*buttons)


def race_detail_button(obj):
    r = obj.race
    btn_race_detail = InlineKeyboardButton(
        text=REG_BUTTONS['race_detail'],
        callback_data=f'race_detai:{r["id"]}')
    return InlineKeyboardMarkup().add(btn_race_detail)
