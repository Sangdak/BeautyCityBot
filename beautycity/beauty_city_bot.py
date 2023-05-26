import os
import django
import re

from beautycity.settings import TG_BOT_TOKEN

from aiogram import Bot, Dispatcher
from aiogram.types import (Message, KeyboardButton, ReplyKeyboardMarkup,
                           InlineKeyboardButton, InlineKeyboardMarkup,
                           ReplyKeyboardRemove, CallbackQuery)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import CommandStart, Text


os.environ['DJANGO_SETTINGS_MODULE'] = 'beautycity.settings'
django.setup()


bot: Bot = Bot(TG_BOT_TOKEN)
dp: Dispatcher = Dispatcher()


schedule = {'25.05': {'10:00': ('Ольга', 'Татьяна'),
                      '10:30': ('Ольга',),
                      '11:00': ('Ольга',),
                      '11:30': ('Татьяна',),
                      '12:00': (),
                      '12:30': (),
                      '13:00': ('Ольга', 'Татьяна',),
                      '13:30': (),
                      '14:00': ('Татьяна',),
                      '14:30': (),
                      '15:00': ('Ольга', 'Татьяна',),
                      '15:30': (),
                      '16:00': ('Ольга',),
                      '16:30': (),
                      '17:00': ('Татьяна',),
                      '17:30': (),
                      '18:00': ('Ольга', 'Татьяна',),
                      '18:30': ('Ольга',),
                      },
            '26.05': {'10:00': ('Ольга',),
                      '10:30': (),
                      '11:00': ('Ольга',),
                      '11:30': (),
                      '12:00': ('Ольга',),
                      '12:30': (),
                      '13:00': (),
                      '13:30': ('Ольга',),
                      '14:00': (),
                      '14:30': (),
                      '15:00': ('Ольга',),
                      '15:30': (),
                      '16:00': ('Ольга',),
                      '16:30': (),
                      '17:00': (),
                      '17:30': ('Ольга',),
                      '18:00': (),
                      '18:30': (),
                      }
            }

prices: dict[str: int] = {'Макияж': 2000,
                          'Покраска волос': 3500,
                          'Маникюр': 800}

users: dict = {}

weekdays: list[str] = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
available_hours: list[str] = []

about_us: KeyboardButton = KeyboardButton(text='О нас')
feedback: KeyboardButton = KeyboardButton(text='Оставить отзыв')
appointment: KeyboardButton = KeyboardButton(text='Записаться на процедуру')
makeup: KeyboardButton = KeyboardButton(text='Макияж')
hair_coloring: KeyboardButton = KeyboardButton(text='Покраска волос')
manicure: KeyboardButton = KeyboardButton(text='Маникюр')
choose_master: KeyboardButton = KeyboardButton(text='Выбрать мастера')
choose_date: KeyboardButton = KeyboardButton(text='Выбрать дату и время')

approval_button: InlineKeyboardButton = InlineKeyboardButton(text='Продолжить',
                                                             callback_data='Продолжить')


main_page_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[
    [appointment], [feedback], [about_us]
    ], resize_keyboard=True)
procedures_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[
    [makeup], [hair_coloring], [manicure]
    ], resize_keyboard=True)
keyboard3: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[
    [choose_master], [choose_date]
    ], resize_keyboard=True)
approval_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[approval_button]])


@dp.message(CommandStart())
async def process_start_command(message: Message):
    if message.from_user.id not in users:
        users[message.from_user.id] = {'first_visit': True,
                                       'procedure': None,
                                       'date': None,
                                       'hour': None,
                                       'master': None,
                                       }
    await message.answer(text='Hello',
                         reply_markup=main_page_keyboard)


@dp.message(Text(text='О нас'))
async def process_about_us_button(message: Message):
    await message.answer(text='Больше, чем салон красоты.\nПредлагает полный '
                         'спектр услуг.\nРежим работы салона с 10:00 до 19:00',
                         reply_markup=main_page_keyboard)


@dp.message(Text(text='Записаться на процедуру'))
async def process_appointment_button(message: Message):
    await message.answer(text='Выберите процедуру:',
                         reply_markup=procedures_keyboard)


@dp.message(Text(text=['Макияж', 'Покраска волос', 'Маникюр']))
async def show_prices(message: Message):
    users[message.from_user.id]['procedure'] = message.text
    await message.answer(text=f'Стоимость услуги {prices[message.text]} рублей.',
                         reply_markup=approval_keyboard)


@dp.callback_query(Text(text='Продолжить'))
async def process_approval(callback: CallbackQuery):
    await callback.answer(text='Принято!')
    await callback.message.answer(text='Выберите мастера и дату',
                                  reply_markup=keyboard3)


@dp.message(Text(text='Выбрать дату и время'))
async def process_date_selection(message: Message):
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    buttons = [KeyboardButton(text=f'{date}') for date in schedule.keys()]
    kb_builder.row(*buttons)
    await message.answer(text='Выберите день:',
                         reply_markup=kb_builder.as_markup(resize_keyboard=True))


@dp.message(lambda msg: re.fullmatch(r'\d\d\.\d\d', msg.text))
async def process_time_selection(message: Message):
    users[message.from_user.id]['date'] = message.text
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    buttons = []
    for hour in schedule[message.text].keys():
        if schedule[message.text][hour]:
            buttons.append(KeyboardButton(text=hour))
        else:
            buttons.append(KeyboardButton(text=' '))
    kb_builder.row(*buttons, width=4)
    await message.answer(text='Выберите свободное время:',
                         reply_markup=kb_builder.as_markup(resize_keyboard=True))


@dp.message(lambda msg: re.fullmatch(r'\d\d\:\d\d', msg.text))  # lambda msg: msg.text in schedule[users[message.from_user.id]['date']].keys()
async def process_master_selection(message: Message):
    users[message.from_user.id]['hour'] = message.text
    await message.reply(text='Отлично!', reply_markup=ReplyKeyboardRemove())
    await message.answer(text=f'\n{users[message.from_user.id]}\nТакого рода словарь можно возвращать обратно в базу')
    # клавиатура с выбором мастера
    # buttons = [KeyboardButton(text=f'{hour}') for hour in schedule[message.text].keys()]
    # kb_builder.row(*buttons, width=4)


# ReplyKeyboardRemove()
if __name__ == '__main__':
    dp.run_polling(bot)
