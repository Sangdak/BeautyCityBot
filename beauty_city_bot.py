from config import TG_BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.types import (Message, KeyboardButton, ReplyKeyboardMarkup,
                           InlineKeyboardButton, InlineKeyboardMarkup,
                           ReplyKeyboardRemove, CallbackQuery)
from aiogram.filters import CommandStart, Text


bot: Bot = Bot(TG_BOT_TOKEN)
dp: Dispatcher = Dispatcher()


prices: dict[str: int] = {'Макияж': 2000,
                          'Покраска волос': 3500,
                          'Маникюр': 800}
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
    await message.answer(text=f'Стоимость услуги {prices[message.text]} рублей.',
                         reply_markup=approval_keyboard)


@dp.callback_query(Text(text='Продолжить'))
async def process_approval(callback: CallbackQuery):
    await callback.answer(text='Принято!')


# ReplyKeyboardRemove()
if __name__ == '__main__':
    dp.run_polling(bot)
