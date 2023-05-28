import os
import django
import re

from beautycity.settings import TG_BOT_TOKEN

from aiogram import Bot, Dispatcher, F
from aiogram.types import (Message, KeyboardButton, ReplyKeyboardMarkup,
                           InlineKeyboardButton, InlineKeyboardMarkup,
                           ReplyKeyboardRemove, CallbackQuery)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.filters import CommandStart, Text, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state


os.environ['DJANGO_SETTINGS_MODULE'] = 'beautycity.settings'
django.setup()


storage: MemoryStorage = MemoryStorage()
bot: Bot = Bot(TG_BOT_TOKEN)
dp: Dispatcher = Dispatcher(storage=storage)


class FSM(StatesGroup):
    master_selection = State()
    time_selection = State()
    fill_name = State()
    fill_phone = State()


def get_masters_hours(masters, schedule):
    for master in masters:
        for day, hours in schedule.items():
            lst = []
            for hour in hours:
                if master in schedule[day][hour]:
                    lst.append(hour)
                    masters[master][day] = lst
    return masters


# work_hours = ('10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', )
# weekdays: list[str] = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
# available_hours: list[str] = []

# TODO: get_schedule() - требуется функция, которая будет возвращать коллекцию с расписанием мастеров
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

# TODO: get_masters() - требуется функция, которая будет возвращать коллекцию с именами мастеров
masters = {'Ольга': {},
           'Татьяна': {}}

masters_schedule = get_masters_hours(masters, schedule)

prices: dict[str: int] = {'Макияж': 2000,
                          'Покраска волос': 3500,
                          'Маникюр': 800}

users: dict = {}

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
choose_master_or_date_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(keyboard=[
    [choose_master], [choose_date]
    ], resize_keyboard=True)
approval_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[[approval_button]])


@dp.message(CommandStart())
async def process_start_command(message: Message):
    if message.from_user.id not in users:
        users[message.from_user.id] = {'procedure': None,
                                       'date': None,
                                       'hour': None,
                                       'master': None,
                                       'name': None,
                                       'phone': None
                                       }
    await message.answer(text='Hello',
                         reply_markup=main_page_keyboard)


@dp.message(StateFilter(default_state),
            Text(text='О нас'))
async def process_about_us_button(message: Message):
    await message.answer(text='Больше, чем салон красоты.\nПредлагает полный '
                         'спектр услуг.\nРежим работы салона с 10:00 до 19:00',
                         reply_markup=main_page_keyboard)


@dp.message(StateFilter(default_state),
            Text(text='Записаться на процедуру'))
async def process_appointment_button(message: Message):
    await message.answer(text='Выберите процедуру:',
                         reply_markup=procedures_keyboard)


@dp.message(StateFilter(default_state),
            Text(text=['Макияж', 'Покраска волос', 'Маникюр']))
async def show_prices(message: Message):
    users[message.from_user.id]['procedure'] = message.text
    await message.answer(text=f'Стоимость услуги {prices[message.text]} рублей.',
                         reply_markup=approval_keyboard)


@dp.callback_query(StateFilter(default_state),
                   Text(text='Продолжить'))
async def process_approval(callback: CallbackQuery):
    await callback.answer(text='Принято!')
    await callback.message.answer(text='Выберите мастера и дату',
                                  reply_markup=choose_master_or_date_keyboard)


# случай, когда сначала выбираем мастера
@dp.message(StateFilter(default_state),
            Text(text='Выбрать мастера'))
async def process_master_selection(message: Message, state: FSMContext):
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    buttons = [KeyboardButton(text=master) for master in masters_schedule]
    kb_builder.row(*buttons, width=3)
    await message.answer(text='Выберите мастера:',
                         reply_markup=kb_builder.as_markup(resize_keyboard=True))
    await state.set_state(FSM.master_selection)


# случай, когда сначала выбираем мастера
@dp.message(StateFilter(FSM.master_selection),
            lambda msg: msg.text in masters_schedule)
async def process_master_date_selection(message: Message):
    users[message.from_user.id]['master'] = message.text

    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    buttons = [KeyboardButton(text=date) for date in masters_schedule[message.text]]
    kb_builder.row(*buttons, width=4)
    await message.answer(text='Выберите день:',
                         reply_markup=kb_builder.as_markup(resize_keyboard=True))


# случай, когда сначала выбираем мастера
@dp.message(StateFilter(FSM.master_selection),
            lambda msg: re.fullmatch(r'\d\d\.\d\d', msg.text))
async def process_master_time_selection(message: Message):
    users[message.from_user.id]['date'] = message.text
    master = users[message.from_user.id]['master']
    date = message.text

    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    buttons = []
    for hour in schedule[date].keys():
        if hour in masters_schedule[master][date]:
            buttons.append(KeyboardButton(text=hour))
        else:
            buttons.append(KeyboardButton(text=f'{hour} - н/д'))
    kb_builder.row(*buttons, width=4)
    await message.answer(text='Выберите свободное время:',
                         reply_markup=kb_builder.as_markup(resize_keyboard=True))


# случай, когда сначала выбираем мастера
@dp.message(StateFilter(FSM.master_selection),
            lambda msg: re.fullmatch(r'\d\d\:\d\d', msg.text))
async def process_contact_inf(message: Message, state: FSMContext):
    users[message.from_user.id]['hour'] = message.text
    await message.answer(text='Введите ваше имя:', reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSM.fill_name)


# случай, когда сначала выбираем время
@dp.message(StateFilter(default_state),
            Text(text='Выбрать дату и время'))
async def process_date_selection(message: Message, state: FSMContext):
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    buttons = [KeyboardButton(text=date) for date in schedule.keys()]
    kb_builder.row(*buttons)
    await message.answer(text='Выберите день:',
                         reply_markup=kb_builder.as_markup(resize_keyboard=True))
    await state.set_state(FSM.time_selection)


# случай, когда сначала выбираем время
@dp.message(StateFilter(FSM.time_selection), lambda msg: re.fullmatch(r'\d\d\.\d\d', msg.text))
async def process_time_selection(message: Message):
    users[message.from_user.id]['date'] = message.text
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    buttons = []
    for hour in schedule[message.text].keys():
        if schedule[message.text][hour]:
            buttons.append(KeyboardButton(text=hour))
        else:
            buttons.append(KeyboardButton(text=f'{hour} - н/д'))
    kb_builder.row(*buttons, width=4)
    await message.answer(text='Выберите свободное время:',
                         reply_markup=kb_builder.as_markup(resize_keyboard=True))


# случай, когда сначала выбираем время
@dp.message(StateFilter(FSM.time_selection),
            lambda msg: re.fullmatch(r'\d\d\:\d\d', msg.text))
async def process_time_master_selection(message: Message):
    users[message.from_user.id]['hour'] = message.text
    date = users[message.from_user.id]['date']
    hour = message.text
    kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
    buttons = [KeyboardButton(text=master) for master in schedule[date][hour]]
    kb_builder.row(*buttons, width=4)
    await message.answer(text='Выберите свободного мастера:',
                         reply_markup=kb_builder.as_markup(resize_keyboard=True))


# случай, когда сначала выбираем время
@dp.message(StateFilter(FSM.time_selection),
            lambda msg: msg.text.isalpha())
async def process_contact_inf_2(message: Message, state: FSMContext):
    users[message.from_user.id]['master'] = message.text
    await message.answer(text='Введите ваше имя:\nВводя данные вы даете '
                         'согласие на обработку ваших персональных данных',
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(FSM.fill_name)


@dp.message(StateFilter(FSM.fill_name),
            lambda msg: msg.text.replace(' ', '').isalpha())
async def process_name_input(message: Message, state: FSMContext):
    users[message.from_user.id]['name'] = message.text
    await message.answer(text='Введите ваш номер:')
    await state.set_state(FSM.fill_phone)


@dp.message(StateFilter(FSM.fill_phone))
async def process_phone_input(message: Message, state: FSMContext):
    users[message.from_user.id]['phone'] = message.text
    await message.answer(
        text=f'Вы записаны на "{users[message.from_user.id]["procedure"]}" в '
        f'{users[message.from_user.id]["date"]} в {users[message.from_user.id]["hour"]} часов\n'
        f'Имя мастера: {users[message.from_user.id]["master"]}')
    await state.set_state(default_state)
    # TODO: Функция, которая отправляет собранные в словарь users данные в БД


@dp.message()
async def process_incorrect_input(message: Message):
    await message.answer(text='Ошибка ввода! Пожалуйста, введите корректные данные.')


# StateFilter(default_state)
# ReplyKeyboardRemove()
if __name__ == '__main__':
    dp.run_polling(bot)
