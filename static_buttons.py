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
        callback_data=json.dumps({'race_detail': r["id"]})
        )
    return InlineKeyboardMarkup().add(btn_race_detail)


def reg_update_button(obj):
    reg_code = obj.id
    btn_reg_update = InlineKeyboardButton(
        text=REG_BUTTONS['reg_update'],
        callback_data=json.dumps({'reg_update': reg_code})
        )
    return InlineKeyboardMarkup().add(btn_reg_update)
