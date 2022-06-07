from aiogram import types, Dispatcher
from aiogram.utils.markdown import hbold
from database import sqlite
from loguru import logger
from keyboards import keyboards
from config import path

sql = sqlite.Sqlite(path)

keyboard_markup = None


async def history_keyboards_2(message: types.Message):
    """
    Формируем клавиатуру,
    опираясь на города из истории поиска,
    отправляем ее пользователю
    активация командой /history
    :param message: types.Message
    :return: None
    """

    keyboard_markup = types.InlineKeyboardMarkup(row_width=1).add(keyboards.inline_kb10)
    person_id = message.from_user.id
    result = sql.return_city(person_id)
    text_and_data = (
        (result[0], 'first_city'),
        (result[1], 'second_city'),
        (result[2], 'third_city')
    )
    row_btn = []
    for text, data in text_and_data:
        if text is not None:
            row_btn.append(types.InlineKeyboardButton(text, callback_data=data))
        else:
            break
    keyboard_markup.row(*row_btn)
    await message.answer(f'{hbold("Ваша история поиска:")}\n\nЗдесь представлены последние 3 города,'
                         f' которые вы искали. Выберите один из городов,'
                         f' чтобы посмотреть результат вашего поиска.'
                         f' Если здесь ничего нет, значит вы еще не искали!', reply_markup=keyboard_markup)


async def history_keyboards(callback_query: types.CallbackQuery):
    """
    Формируем клавиатуру,
    опираясь на города из истории поиска,
    отправляем ее пользователю
    активация инлайн клавиатурой
    :param callback_query: types.CallbackQuery
    :return: None
    """

    logger.info(f'Пользователь {callback_query.message.from_user.username} смотрит историю')
    keyboard_markup = types.InlineKeyboardMarkup(row_width=1).add(keyboards.inline_kb10)
    person_id = callback_query.from_user.id
    result = sql.return_city(person_id)
    text_and_data = (
        (result[0], 'first_city'),
        (result[1], 'second_city'),
        (result[2], 'third_city')
    )
    row_btn = []
    for text, data in text_and_data:
        if text is not None:
            row_btn.append(types.InlineKeyboardButton(text, callback_data=data))
        else:
            break
    keyboard_markup.row(*row_btn)
    await callback_query.message.edit_text(f'{hbold("Ваша история поиска:")}\n\nЗдесь представлены последние 3 города,'
                                           f' которые вы искали. Выберите один из городов,'
                                           f' чтобы посмотреть результат вашего поиска.'
                                           f' Если здесь ничего нет, значит вы еще не искали!',
                                           reply_markup=keyboard_markup)


async def city_history(callback_query: types.CallbackQuery):
    """
    Принимаем ответ от пользователя,
    выводим историю поиска
    :param callback_query: types.CallbackQuery
    :return: None
    """
    answer_data = callback_query.data
    logger.info(f'Date: {answer_data}')
    person_id = callback_query.from_user.id
    if answer_data == 'first_city':
        res = sql.return_first_city_history(person_id)
    elif answer_data == 'second_city':
        res = sql.return_second_city_history(person_id)
    else:
        res = sql.return_third_city_history(person_id)
    try:
        await callback_query.message.edit_text(res)
        await callback_query.message.edit_reply_markup(reply_markup=keyboards.inline_buttons_6)
    except Exception as exc:
        await callback_query.message.answer('Здесь боту ничего не удалось найти!')
        logger.error(f"Возникла ошибка: {exc}")


async def back_button_3(callback_query: types.CallbackQuery):
    """
    Вторая инлайн кнопка назад,
    чтобы вернутся в главное меню
    :param callback_query: types.CallbackQuery
    :return: None
    """
    await callback_query.message.edit_text(f'{hbold("Ваша история поиска:")}\n\nЗдесь представлены последние 3 города,'
                                           f' которые вы искали. Выберите один из городов,'
                                           f' чтобы посмотреть результат вашего поиска.'
                                           f' Если здесь ничего нет, значит вы еще не искали!')
    await callback_query.message.edit_reply_markup(reply_markup=keyboard_markup)


def register_history_handler(dp: Dispatcher):
    """
    Регистрируем хэндлеры
    :param dp:
    :return: None
    """
    dp.register_callback_query_handler(history_keyboards, text='button_4')
    dp.register_message_handler(history_keyboards_2, commands=['history'])
    dp.register_callback_query_handler(city_history, text='first_city')
    dp.register_callback_query_handler(city_history, text='second_city')
    dp.register_callback_query_handler(city_history, text='third_city')
    dp.register_callback_query_handler(back_button_3, text='Back_3')
