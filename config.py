
MESSAGES = {
    'welcome':
        'Приветствую! Помогу подать заявку на участие.\n'
        'в соревнованиях. Подробности по команде /help',
    'no_finished_commands': 'У Вас есть незавершенные процессы: %s',
    'not_allowed_btn': 'Нажатая кнопка не используется'
                       'в текущем процессе',
    'cmd_always_on': 'Эта команда уже выполняется! Ожидаю ввод данных.',
    'mess_cancel_this': 'команда {} отменена',
    'mess_cancel_all': 'все процессы прекращены',
}

BUTTONS = {
    'btn_make_registr': 'Подать_заявку',
    'cancel_this': 'Прекратить',
    'cancel_all': 'Отменить_все',
    'all_races': 'Все_мероприятия',
}

REG_MESSAGE = {
    'race_not_found': 'Мероприятие с указанным идентификатором не найдено',
    'category_not_found': 'Выбрана категория, не относящаяся'
                          ' к этому мероприятию',
    'conection_error': 'Сервер регистрации не доступен. Попробуйте'
                       ' повторить отправку позднее',
    'step_is_required': 'Этот шаг нельзя пропускать.'
                        ' Информация необходима для заявки.',
    'unknown_reg_error': 'Сервер не принял заявку по неизвестной причине',
    'not_integer': 'Необходимо ввести число. Повторите ввод!',
    'not_dict': 'Ожидаются данные от нажатия кнопки, а не от ввода текста!',
    'no_category_data': 'Была нажата кнопка, не относящаяся к категории.'
                        ' Повторите ввод!',
    'mess_ask_race': 'Введите идентификатор мероприятия',
    'mess_ask_name': 'Введите имя участника',
    'mess_ask_surname': 'Введите фамилию участника',
    'mess_ask_patronymic': 'Введите отчество участника',
    'mess_ask_year': 'Введите год рождения участника',
    'mess_ask_town': 'Введите название города участника',
    'mess_ask_club': 'Введите название клуба, за который '
                      'выступает участник',
    'mess_ask_category': 'Выберите категорию участника',
    'mess_ask_number': 'Введите желаемый стартовый номер',

}

REG_BUTTONS = {
    'race_detail': 'Подробно о событии',
    'pass': 'Пропустить',
    'reg_update': 'Редактировать заявку',
    'reg_start': 'Зарегистрироваться',

}

ALLOWED_BUTTONS = {
    'registration': ['pass', 'category', 'reg_start'],
    'show_all_races': ['prev', 'next'],
}


ABOUT_RACE = ('*Название:* {},\n'
              '*Дата проведения:* {},\n'
              '*Группа мероприятий:* {},\n'
              '*Место проведения:* {},\n'
              '*Категории участников:* \n{},\n'
              '*Подробное описание:* \n{},\n'
              )
