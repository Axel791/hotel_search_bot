from keyboards import keyboards
from aiogram import types, Dispatcher
from aiogram.utils.markdown import hbold
from loguru import logger
from database import sqlite
from aiogram.dispatcher import FSMContext
from config import path


sql = sqlite.Sqlite(path)


async def start_commands(message: types.Message):
    """
    Начало работы бота, команда /start
    :param message: types.Message
    :return: None
    """

    await message.answer(f'{hbold(f"Привет, {message.from_user.first_name}!")} '
                         f'Я-бот, сделанный на основе сайта Hotels.com,'
                         f' который поможет найти тебе отель в любой точке мира!\n\n'
                         f'{hbold("Как мною пользоваться?")}'
                         f'\n\n/low_price-поиск отелей с самой низкой ценой за ночь.'
                         f'\n/best_deal-поиск лучших отелей, зависящих от введенных вами критериев.'
                         f'\n/history-просмотр вашей истории поиска.'
                         f'\n/high_price-просмотр отелей с самой высокой ценой за ночь.'
                         , reply_markup=keyboards.keyboard)
    logger.info('Пользователь нажал команду start')
    sql.add_user(message.from_user.id)

    await message.answer('Перед вами главное меню:⬇        ', reply_markup=keyboards.inline_buttons_5)


async def forming_the_main_menu(callback_query: types.CallbackQuery):
    """
    Главное меню бота,
    отправка его пользователю
    :param callback_query: types.Message
    :return: None
    """
    await callback_query.message.edit_text('Выберите один пункт из списка ниже⬇️',
                                           reply_markup=keyboards.inline_buttons_1)
    logger.info('Пользователь нажал на кнопку "Найти отели"')


async def forming_the_back_to_functions_button(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Формируем кнопку назад в главном меню
    для более удобной работы с инлайн клавиатурой
    :param callback_query: types.callbackQuery
    :param state: FSMContext
    :return: None
    """
    await callback_query.message.edit_reply_markup(reply_markup=keyboards.inline_buttons_1)
    await state.finish()
    await callback_query.message.answer('Поиск отменен, для продолжения выберите 1 из пунктов...✖')


async def form_the_back_button_to_the_main_menu(callback_query: types.CallbackQuery):
    """
    Вторая инлайн кнопка назад,
    чтобы вернутся в главное меню
    :param callback_query: types.CallbackQuery
    :return: None
    """
    await callback_query.message.edit_text('Перед вами главное меню:⬇       ')
    await callback_query.message.edit_reply_markup(reply_markup=keyboards.inline_buttons_5)


async def opening_main_menu(message: types.Message):
    """
    Активация главного меню
    :param message: types.Message
    :return: None
    """
    await message.answer('Перед вами главное меню:⬇        ', reply_markup=keyboards.inline_buttons_5)


def register_welcome_handler(dp: Dispatcher):
    """
    Регистрируем хэндлеры
    :param dp: Dispatcher
    :return: None
    """
    dp.register_message_handler(start_commands, commands=['start'])
    dp.register_callback_query_handler(forming_the_main_menu, text='find_hotels')
    dp.register_callback_query_handler(forming_the_back_to_functions_button, text='Back', state='*')
    dp.register_callback_query_handler(form_the_back_button_to_the_main_menu, text='Back_2')
    dp.register_message_handler(opening_main_menu, lambda message: message.text == 'Главное меню')
