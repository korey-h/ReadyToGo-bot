import os
from datetime import datetime as dt

from config import DEBUG_MODE


def log_to_file(user_id: int, rec_type: str, text: str):
    if not DEBUG_MODE:
        return
    log_dir = 'chat_loggs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    file_name = f'{log_dir}/{str(user_id)}.txt'
    point = dt.now().strftime("%Y-%m-%d  %H:%M:%S")
    with open(file_name, 'a') as f:
        f.write('  '.join([point, rec_type + ' >>>', text + '\n']))


def com_logger(message):
    user_id = message.chat.id
    log_to_file(user_id, 'command', message.text)
    return message


def query_logger(call):
    message = call.message
    user_id = message.chat.id
    text = call.data
    log_to_file(user_id, 'inline_button', text)
    return call


def text_logger(message):
    user_id = message.chat.id
    log_to_file(user_id, 'from_keyboard', message.text)
    return message
