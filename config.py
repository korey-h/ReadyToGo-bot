import os

from dotenv import load_dotenv

if os.path.exists('.env'):
    load_dotenv('.env')

PAGE_LIMIT = 10
DEBUG_MODE = True
HOST = 'http://' + os.environ.get('HOST') + '/api/v1'

MESSAGES = {
    'welcome':
        'Приветствую! Помогу подать заявку на участие.\n'
        'в соревнованиях. Подробности по команде /help',
    'lets_reg': 'Приветствую!',
    'no_finished_commands': 'У Вас есть незавершенный процесс: %s. '
                            'Для выполнения команды нужно его прекратить.',
    'not_allowed_btn': 'Нажатая кнопка не используется '
                       'в текущем процессе',
    'cmd_always_on': 'Эта команда уже выполняется! Ожидаю ввод данных.',
    'mess_cancel_this': 'Команда "{}" отменена',
    'mess_cancel_all': 'Все процессы прекращены',
    'mess_finded_races': 'Мероприятия с активной регистрацией '
                         '(часть {} из {}).',
    'conection_error': 'Сервер регистрации недоступен. Попробуйте'
                       ' повторить запрос позднее',
    'not_found': 'Информация отсутствует!',
    'unknown_error': 'Что-то пошло не так. Попробуйте позднее.',
}

BUTTONS = {
    'btn_make_registr': 'Подать_заявку',
    'btn_reg_update': 'Редактировать_заявку',
    'cancel_this': 'Прекратить',
    'cancel_all': 'Отменить_все',
    'all_races': 'Все_мероприятия',
    'next': 'Показать еще',
    'name': 'Имя',
    'surname': 'Фамилия',
    'patronymic': 'Отчество',
    'year': 'Год',
    'number': 'Номер',
    'club': 'Клуб',
    'town': 'Город',
    'category': 'Категория',
    'save': 'Сохранить изменения',
    'save_changes': 'Сохранить',
}

REG_MESSAGE = {
    'race_not_found': 'Мероприятие с указанным идентификатором не найдено',
    'reg_not_found': 'Заявка с введенным идентификатором не найдена.',
    'category_not_found': 'Выбрана категория, не относящаяся'
                          ' к этому мероприятию',
    'conection_error': 'Сервер регистрации недоступен. Попробуйте'
                       ' повторить отправку позднее',
    'step_is_required': 'Этот шаг нельзя пропускать.'
                        ' Информация необходима для заявки.',
    'unknown_reg_error': 'Сервер не принял заявку по неизвестной причине. '
                         'Прекратите текущую регистрацию и '
                         'попробуйте подать заявку позднее.',
    'unknown_fild_error': 'При обработке заявки возникла неизвестная ошибка'
                         'Прекратите текущую регистрацию и '
                         'попробуйте подать заявку позднее.',
    'not_integer': 'Необходимо ввести число. Повторите ввод!',
    'not_dict': 'Ожидаются данные от нажатия кнопки, а не от ввода текста!',
    'no_category_data': 'Была нажата кнопка, не относящаяся к категории.'
                        ' Повторите ввод!',
    'mess_ask_race': 'Введите идентификатор мероприятия '
                     'или выберите мероприятие из списка '
                     f'по команде /{BUTTONS["all_races"]}',
    'mess_ask_name': 'Введите имя участника',
    'mess_ask_surname': 'Введите фамилию участника',
    'mess_ask_patronymic': 'Введите отчество участника',
    'mess_ask_year': 'Введите год рождения участника',
    'mess_ask_town': 'Введите название города участника',
    'mess_ask_club': 'Введите название клуба, за который '
                      'выступает участник',
    'mess_ask_category': 'Выберите категорию участника',
    'mess_ask_number': 'Введите желаемый стартовый номер',
    'reg_always_on': 'Уже запущена регистрация на "{}".'
                      'Ожидаю ввод данных.',
    'mess_reg_id': 'Введите номер заявки, полученный после регистрации',
    'mess_data_upd': f'Данные обновлены. /{BUTTONS["save_changes"]} ?',
    'mess_select_edit_btn': 'Нажмите на кнопку с данными для их изменения. '
                            'После внесения всех необходимых изменений '
                            'потребуется отправить команду'
                            f' /{BUTTONS["save_changes"]}',
    'lets_reg': 'Для предстартовой регистрации на "%s" '
                'нужна некоторая информация об участнике.',
    'reg_confirm': 'Событие: %s\n'
                   'Участник: %s %s %s, %s г.р.\n'
                   'Город: %s\n'
                   'Клуб: %s\n'
                   'Категория: %s\n'
                   'Стартовый номер: %s\n'
                   'Номер заявки (для редактирования):\n'
                   '%s',
    'reg_inactive': 'Регистрация на мероприятие прекращена',

}

REG_BUTTONS = {
    'race_detail': 'Подробно о событии',
    'pass': 'Пропустить',
    'reg_update': 'Редактировать заявку',
    'reg_start': 'Зарегистрироваться',
    'reg_resend': 'Повтор отправки',

}

ALLOWED_BUTTONS = {
    'registration': ['pass', 'category', 'reg_start', 'reg_resend'],
    'show_all_races': ['prev', 'next'],
    'update_registration': ['reg_upd', 'category', 'reg_resend'],
}


ABOUT_RACE = ('*Название:* {},\n'
              '*Дата проведения:* {},\n'
              '*Группа мероприятий:* {},\n'
              '*Место проведения:* {},\n'
              '*Категории участников:* \n{},\n'
              '*Подробное описание:* \n{},\n'
              )

EMOJI = {'bicyclist': '\U0001F6B4', }
