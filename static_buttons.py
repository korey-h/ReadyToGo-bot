import json

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

from config import BUTTONS, REG_BUTTONS
# from models import RegUpdateProces


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
         BUTTONS['btn_reg_update'],
         BUTTONS['cancel_this'],
         BUTTONS['cancel_all'], ]
        )
    return make_base_kbd(buttons_name, row_width)


def cancel_this_kbd(*args, **kwargs):
    buttons_name = name_to_cmd([
         BUTTONS['cancel_this']
        ])
    return make_base_kbd(buttons_name)


def upd_comms_kbd(*args, **kwargs):
    buttons_name = name_to_cmd([
         BUTTONS['cancel_this'],
         BUTTONS['save_changes'],
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
        obj_year = obj.reg_blank['year']
        year_old = category['year_old']
        year_yang = category['year_yang']
        ages = range(year_old, year_yang + 1)
        if obj_year in ages:
            text = category['name']
            callback_data = json.dumps(
                {'name': 'category',
                 'race_id': obj.race['id'],
                 'cat_id': category['id']}
            )
            button = InlineKeyboardButton(
                text=text,
                callback_data=callback_data)
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


def make_resend_btn(obj):
    callback_data = json.dumps(
            {'name': 'reg_resend',
             'id': obj.reg_blank_id}
        )
    button = InlineKeyboardButton(
        text=REG_BUTTONS['reg_resend'],
        callback_data=callback_data)
    return InlineKeyboardMarkup().add(button)


def races_buttons(races: list, cur_page: int, pages: int = 1):
    datas = []
    for item in races:
        tail = ', ' + item['cup_name'] if item['cup_name'] else ''
        btn_name = item['name'] + tail
        payload = {'name': 'race_data', 'race_id': item['id']}
        datas.append(
            (btn_name, payload)
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
             'id': reg_code})
        )
    return InlineKeyboardMarkup().add(btn_reg_update)


def reg_start_button(race_id):
    btn_reg_update = InlineKeyboardButton(
        text=REG_BUTTONS['reg_start'],
        callback_data=json.dumps(
            {'name': 'reg_start',
             'id': race_id})
        )
    return InlineKeyboardMarkup().add(btn_reg_update)


def upd_data_btns(obj):
    '''obj - объект класса RegUpdateProces'''
    step_for_name = obj._get_step_names()
    reg_blank = obj.reg_blank
    categories = obj.race['race_categories']
    cat_names = {cat['id']: cat['name'] for cat in categories}
    excluded = ['race', 'id', 'reg_code']
    datas = []
    for name, data in reg_blank.items():
        if name in excluded:
            continue
        mark = BUTTONS[name] if BUTTONS.get(name) else name
        value = data if data else '---'
        if name == 'category':
            value = cat_names[data]
        btn_name = f'{mark}: {value}'
        payload = {'name': 'reg_upd', 'step': step_for_name[name]}
        datas.append(
            (btn_name, payload)
        )
    datas.append((
        BUTTONS['save'],
        {'name': 'reg_upd', 'step': obj._finish_step}
        ))
    buttons = make_inline_buttons_row(datas)
    return InlineKeyboardMarkup(row_width=1).add(*buttons)
