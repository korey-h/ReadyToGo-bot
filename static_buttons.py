from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from .config import REG_BUTTONS

pass_button = InlineKeyboardButton(
    text=REG_BUTTONS['pass'],
    callback_data='pass')

pass_keyboard = InlineKeyboardMarkup().add(pass_button)
