from typing import List

import message_generators as mg
import static_buttons as sb

from api_handlers import (
    get_race_detail, race_detail_handler, get_rec_detail, rec_detail_handler,
    send_registration, upd_registration)
from config import EMOJI, REG_MESSAGE


class RegistrProces:

    def __init__(self) -> None:
        self.step = 0
        self.race = None
        self.id = None
        self.is_active = True
        self.errors = {}
        self._fix_list = []
        self.detail_getter = get_race_detail
        self.detail_handler = race_detail_handler
        self.reg_sender = send_registration
        self.reg_blank = {
            'race': None,
            'category': None,
            'name': '',
            'surname': '',
            'patronymic': '',
            'number': None,
            'year': None,
            'club': '',
            'town': ''
        }

    _stop_text = 'to registration'
    _finish_step = 10
    _prior_messages = {
        1: [{'text': REG_MESSAGE['mess_ask_race'],
            'kbd_maker': sb.cancel_this_kbd}],
        2: [{'text': mg.about_reg,
             'kbd_maker': sb.cancel_this_kbd},
            {'text': REG_MESSAGE['mess_ask_name'],
            'kbd_maker': sb.race_detail_button}],
        3: [{'text': REG_MESSAGE['mess_ask_surname']}],
        4: [{'text': REG_MESSAGE['mess_ask_patronymic'],
            'kbd_maker': sb.pass_keyboard}],
        5: [{'text': REG_MESSAGE['mess_ask_year']}],
        6: [{'text': REG_MESSAGE['mess_ask_town'],
            'kbd_maker': sb.pass_keyboard}],
        7: [{'text': REG_MESSAGE['mess_ask_club'],
            'kbd_maker': sb.pass_keyboard}],
        8: [{'text': REG_MESSAGE['mess_ask_category'],
            'kbd_maker': sb.category_keyboard}],
        9: [{'text': REG_MESSAGE['mess_ask_number']}],
        10: [{'text': _stop_text}],
    }

    _step_actions = {
        1: {'name': 'race', 'required': True},
        2: {'name': 'name', 'required': True},
        3: {'name': 'surname', 'required': True},
        4: {'name': 'patronymic', 'required': False},
        5: {'name': 'year', 'required': True},
        6: {'name': 'town', 'required': False},
        7: {'name': 'club', 'required': False},
        8: {'name': 'category', 'required': True},
        9: {'name': 'number', 'required': True},
        10: {'name': 'registration', 'required': True},
    }

    def _get_action(self, step: int) -> dict:
        return self._step_actions.get(step)

    def _get_step_names(self) -> dict:
        return {
            val['name']: st for st, val in self._step_actions.items()
        }

    def _get_validator(self, step: int):
        validators = {
            1: self._race_setter,
            2: self._clipper,
            3: self._clipper,
            4: self._clipper,
            5: self._to_integer,
            6: self._clipper,
            7: self._clipper,
            8: self._to_category,
            9: self._to_integer,
        }
        return validators.get(step)

    def is_act_required(self):
        act = self._get_action(self.step)
        return act['required']

    def pass_step(self):
        if self.is_act_required():
            return self.mess_wrapper(REG_MESSAGE['step_is_required'])
        self.step += 1
        return self.mess_wrapper(self.step)

    def repeat_last_step(self):
        if self.step > 0:
            self.step -= 1
        return self.exec()

    def step_handler(self, data) -> dict:
        if data is not None:
            validator = self._get_validator(self.step)
            if validator:
                res = validator(data)
                if res['error']:
                    return self.mess_wrapper(res['error'])
                data = res['data']

            act = self._get_action(self.step)
            if act:
                entry = act['name']
                self.reg_blank[entry] = data

        if self.step == 1 and not self.race['is_active']:
            self.is_active = False
            return self.mess_wrapper(
                {'text': REG_MESSAGE['reg_inactive'],
                 'reply_markup': sb.make_welcome_kbd()})

        if not self._fix_list:
            self.step += 1
        else:
            self.step = self._fix_list.pop()
        return self.mess_wrapper(self.step)

    def exec(self, data=None) -> dict:
        res = self.step_handler(data)
        if self.step == self._finish_step:
            return self.make_registration()
        return res

    def make_registration(self) -> dict:
        res = self.reg_sender(self.reg_blank)
        res_data = res.get('data')
        if res['status'] in (200, 201):
            self.id = res_data['reg_code']
            self.is_active = False
            r = self.race
            bl = self.reg_blank
            cat_names = {c['id']: c['name'] for c in r['race_categories']}
            text = REG_MESSAGE['reg_confirm'] % (
                    r["name"], bl["name"],
                    bl["patronymic"], bl["surname"], bl["year"], bl["town"],
                    bl["club"], cat_names[bl["category"]], bl["number"],
                    self.id)

            keyboard = sb.reg_update_button(self)
            return self.mess_wrapper([
                [text, keyboard],
                [EMOJI['bicyclist'], sb.make_welcome_kbd()],
                ])

        elif res['status'] == 400:
            names_w_err = res_data
            step_names = self._get_step_names()

            base_set = set(self.reg_blank.keys())
            cheking_set = set(names_w_err.keys())
            if not cheking_set.issubset(base_set):
                return self.mess_wrapper(
                    {'text': REG_MESSAGE['unknown_fild_error']}
                    )

            for name, errs in names_w_err.items():
                step = step_names[name]
                self._fix_list.append(step)
                self.errors[step] = ';'.join(errs)
            self._fix_list.append(self._finish_step)
            self._fix_list.reverse()
            self.step = self._fix_list.pop()
            text = (self._prior_messages[self.step][0]['text'] + '\n' +
                    self.errors[self.step])
            return self.mess_wrapper(text)

        elif res['status'] == 403:
            self.is_active = False
            keyboard = sb.make_welcome_kbd()
            if isinstance(res_data, str):
                text = res_data
            elif isinstance(res_data, dict):
                text = '\n'.join(res_data.values())
            else:
                text = str(res_data)
            return self.mess_wrapper(
                    {'text': text, 'reply_markup': keyboard}
                    )

        elif res['status'] in range(500, 600):
            return self.mess_wrapper(REG_MESSAGE['conection_error'])
        # TODO: добавить вывод кнопки для повторной отправки заявки.

        return self.mess_wrapper({'text': REG_MESSAGE['unknown_reg_error']})

    def mess_wrapper(self, value) -> List[dict]:
        keyboard = None
        text = None
        if isinstance(value, str):
            text = value
        elif isinstance(value, int):
            pre_mess = []
            datas = self._prior_messages[value]
            for data in datas:
                text = data['text']
                if callable(text):
                    text = text(self)
                maker = data.get('kbd_maker')
                keyboard = maker(self) if maker else None
                pre_mess.append({'text': text, 'reply_markup': keyboard})
            return pre_mess
        elif isinstance(value, (list, tuple)):
            pre_mess = []
            for data in value:
                text = data[0]
                keyboard = data[1]
                pre_mess.append({'text': text, 'reply_markup': keyboard})
            return pre_mess
        elif isinstance(value, dict):
            return [value]
        return [{'text': text, 'reply_markup': keyboard}]

    def _clipper(self, data: str) -> dict:
        data = data.strip()
        return {'data': data, 'error': None}

    def _to_integer(self, data: str) -> dict:
        message = None
        try:
            data = int(data)
        except Exception:
            data = None
            message = REG_MESSAGE['not_integer']
        return {'data': data, 'error': message}

    def _to_category(self, data: dict) -> dict:
        if not isinstance(data, dict):
            return {'data': None,
                    'error': REG_MESSAGE['not_dict']}
        category_id = data.get('cat_id')
        categories = self.race['race_categories']
        if (category_id is None or
                category_id not in [cat['id'] for cat in categories]):
            return {'data': category_id,
                    'error': REG_MESSAGE['no_category_data']}

        return {'data': category_id, 'error': None}

    def _race_setter(self, data) -> dict:
        res = self._to_integer(data)
        if res['error']:
            return res
        race_id = res['data']
        detail = self.detail_handler(race_id, self.detail_getter)
        if detail['error']:
            return detail
        self.race = detail['data']
        return {'data': self.race['id'], 'error': None}


class RegUpdateProces(RegistrProces):
    _stop_text = 'to registration'
    _prior_messages = {
        1: [{'text': REG_MESSAGE['mess_reg_id'],
            'kbd_maker': sb.cancel_this_kbd}],
        2: [{'text': REG_MESSAGE['mess_ask_name'], }],
        3: [{'text': REG_MESSAGE['mess_ask_surname']}],
        4: [{'text': REG_MESSAGE['mess_ask_patronymic'], }],
        5: [{'text': REG_MESSAGE['mess_ask_year']}],
        6: [{'text': REG_MESSAGE['mess_ask_town'], }],
        7: [{'text': REG_MESSAGE['mess_ask_club'], }],
        8: [{'text': REG_MESSAGE['mess_ask_category'],
            'kbd_maker': sb.category_keyboard}],
        9: [{'text': REG_MESSAGE['mess_ask_number']}],
        10: [{'text': _stop_text}],
    }

    def __init__(self) -> None:
        super().__init__()
        self.rec_getter = get_rec_detail
        self.rec_detail_handler = rec_detail_handler
        self.reg_sender = upd_registration

    def pass_step(self):
        pass

    def step_handler(self, data) -> dict:
        if data is None:
            self.step = 1
            return self.mess_wrapper(self.step)
        validator = self._get_validator(self.step)
        if validator:
            res = validator(data)
            if res['error']:
                return self.mess_wrapper(res['error'])
            data = res['data']
        act = self._get_action(self.step)
        if act:
            entry = act['name']
            self.reg_blank[entry] = data
        if self._fix_list:
            self.step = self._fix_list.pop()
            return self.mess_wrapper(self.step)
        if self.step == 1:
            # if not self.race['is_active']:
            #     self.is_active = False
            #     return self.mess_wrapper([
            #         [REG_MESSAGE['reg_inactive'], sb.make_welcome_kbd()]
            #         ])
            return self.mess_wrapper([
                [REG_MESSAGE['mess_select_edit_btn'], sb.upd_data_btns(self)],
                [EMOJI['bicyclist'], sb.upd_comms_kbd()],
                ])
        return self.mess_wrapper(REG_MESSAGE['mess_data_upd'])

    def _race_setter(self, data) -> dict:
        reg_code = data
        rec_detail = self.rec_detail_handler(reg_code, self.rec_getter)
        if rec_detail['error']:
            return rec_detail
        self.reg_blank = rec_detail['data']
        self.id = self.reg_blank['reg_code']
        race_detail = self.detail_handler(
            self.reg_blank['race'], self.detail_getter)
        if race_detail['error']:
            return rec_detail
        self.race = race_detail['data']
        return {'data': self.reg_blank['race'], 'error': None}


class User:
    reg_proces_class = RegistrProces
    reg_update_class = RegUpdateProces

    def __init__(self, id):
        self.id = id
        self._commands = []
        self.reg_proces = None

    def is_stack_empty(self):
        return len(self._commands) == 0

    def get_cmd_stack(self):
        if len(self._commands) > 0:
            return self._commands[-1]
        return []

    def set_cmd_stack(self, cmd_stack):
        if isinstance(cmd_stack, dict):
            self._commands.append(cmd_stack)
        else:
            keys = ('cmd_name', 'cmd', 'data', 'called_by')
            if isinstance(cmd_stack, (list, tuple)):
                s = tuple(cmd_stack)
                keys_am = len(keys)
                values = s[:keys_am] if len(s) >= keys_am else (
                    s + tuple({} for _ in range(keys_am - len(s)))
                    )
            else:
                values = (cmd_stack, cmd_stack, {}, None)
            self._commands.append(
                {key: val for key, val in zip(keys, values)}
            )

    cmd_stack = property(get_cmd_stack, set_cmd_stack)

    def clear_stack(self):
        self._commands.clear()

    def cancel_all(self):
        self.clear_stack()
        self.reg_proces = None

    def cmd_stack_pop(self):
        if len(self._commands) > 0:
            if self.reg_proces:
                self.stop_registration()
            return self._commands.pop()
        return None

    def start_registration(self):
        self.reg_proces = self.reg_proces_class()
        return None

    def update_registration(self):
        self.reg_proces = self.reg_update_class()
        return None

    def stop_registration(self):
        self.reg_proces = None
        return None
