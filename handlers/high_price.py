import re

from config import path
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hbold
from utils import rapid_hotels_api
from loader import bot
from keyboards import keyboards
from loguru import logger
from database import sqlite

sql = sqlite.Sqlite(path)


class WaiteCityAndCount2(StatesGroup):
    """
    Формируем класс,
    где будем хранить состояния
    """
    waite_city_state2 = State()
    waite_photo_answer2 = State()
    waite_photo_count2 = State()
    waite_date_state2 = State()
    waite_count_state2 = State()


async def started_high_price_2(message: types.Message):
    """
    Запрашиваем у пользователя название города,
    активация через команду /high_price
    :param message: types.Message
    :return: None
    """
    await message.answer('Напишите название города🏢:  ')
    await WaiteCityAndCount2.waite_city_state2.set()


async def started_high_price(callback_query: types.CallbackQuery):
    """
    Запрашиваем у пользователя название города,
    активация через инлайн клавиатуру
    :param callback_query: types.CallbackQuery
    :return: None
    """
    logger.info(f"Пользователь: {callback_query.from_user.username} смотрит high_price")
    await callback_query.message.edit_text('Напишите название города🏢:  ')
    await callback_query.message.edit_reply_markup(reply_markup=keyboards.inline_buttons_3)
    await WaiteCityAndCount2.waite_city_state2.set()


async def waite_city_state_2(message: types.Message, state: FSMContext):
    """
    Проверка на корректность города,
    запрашиваем у пользователя необходимость фотографий
    сохраняем город в словарь
    :param message: types.Message
    :param state: FSMContext
    :return: None
    """
    if not message.text.isdigit():
        await state.update_data(city=message.text)
        await message.answer('Вам показать фотографии найденных отелей?', reply_markup=keyboards.inline_buttons_2)
        await WaiteCityAndCount2.waite_photo_answer2.set()
    else:
        await message.answer('Введите название города буквами!')


async def waite_photo_state_2(callback_query: types.CallbackQuery, state: FSMContext):
    """
    В зависимости от ответа пользователя запрашиваем кол-во фото или кол-во отелей,
    так же переходим к следующему состоянию в зависимости от ответа
    :param callback_query: types.CallbackQuery
    :param state: FSMContext
    :return: None
    """
    photo_data = callback_query.data
    await state.update_data(photo=photo_data)
    await callback_query.message.edit_reply_markup()
    if photo_data == 'yes':
        await callback_query.message.answer('Сколько фото вам показать?', reply_markup=keyboards.inline_buttons_4)
        await WaiteCityAndCount2.waite_photo_count2.set()
    else:
        await WaiteCityAndCount2.waite_date_state2.set()
        await callback_query.message.answer('Введите дату заселения и дату выезда как в примере'
                                            f'{hbold("ДД.ММ.ГГ-ДД.ММ.ГГ")}', reply_markup=keyboards.inline_buttons_4)


async def waite_count_photo_state_2(message: types.Message,  state: FSMContext):
    """
    Запрашиваем у пользователя дату,
    проверяем на корректность,
    сохраняем кол-во фото в словарь,
    если пользователь ответил положительно
    :param message: types.Message
    :param state: FSMContext
    :return: None
    """
    if message.text.isdigit():
        await message.answer('Введите дату заселения и дату выезда как в примере'
                             f'{hbold("ДД.ММ.ГГ-ДД.ММ.ГГ")}', reply_markup=keyboards.inline_buttons_4)
        await state.update_data(count_photo=message.text)
        await WaiteCityAndCount2.waite_date_state2.set()


async def waite_date(message: types.Message, state: FSMContext):
    """
    Принимаем дату, проверяем ее на корректность,
    запрашиваем у пользователя кол-во отелей.
    :param message: types.Message
    :param state: FSMContext
    :return: None
    """
    date = re.findall(r"[0-9]*?[0-9]+", message.text)
    logger.info(date)
    if ((len(date) == 6) and (date is not None)
            and (int(date[1]) <= int(date[4])) and (int(date[2]) <= int(date[5]))):
        logger.info('Дата сохранена!')
        await message.answer('Сколько отелей вам показать?', reply_markup=keyboards.inline_buttons_4)
        await state.update_data(date=date)
        await WaiteCityAndCount2.waite_count_state2.set()
    else:
        await message.answer('Дата введена некорректно!')


async def watch_hotels_2(message: types.Message, state: FSMContext):
    """
    Проверяем на корректность введенные данные,
    отправляем пользователю все найденные отели,
    которые соответствуют параметрам
    :param message: types.Message
    :param state: FSMContext
    :return: None
    """
    person_id = message.from_user.id
    if message.text.isdigit():
        await state.update_data(count=message.text)
        user_data = await state.get_data()
        history_dict = {"city": None, "search_results": []}
        logger.info(f"Выбор пользователя {message.from_user.username}: {user_data['city']},"
                    f" {user_data['photo']}, {message.text}")
        await message.answer('Идет поиск, подождите пару секунд...⌛️')
        try:
            full_info = rapid_hotels_api.get_id(user_data["city"], "PRICE_HIGHEST_FIRST")
            return_info = full_info[0]["data"]["body"]["searchResults"]["results"]
            history_dict["city"] = full_info[1]
            for index in range(0, int(user_data["count"])):
                price = (((int(user_data["date"][0]) + int(user_data["date"][3])) +
                          (30 * (int(user_data["date"][4]) - int(user_data["date"][1]))))
                         * return_info[index]["ratePlan"]["price"]["exactCurrent"])
                logger.info(f'{price}')
                answer = (f'{hbold(return_info[index]["name"])}'
                          f'\n\nАдрес:  {return_info[index]["address"]["streetAddress"]}'
                          f'\nРасстояние до центра:  {return_info[index]["landmarks"][0]["distance"]}'
                          f'\nРейтинг:  {return_info[index]["starRating"]}'
                          f'\nЦена:  {round(price, 2)}RUB')
                history_dict["search_results"].append(answer)
                await message.answer(answer)
                if user_data["photo"] == 'yes':
                    for i in range(0, int(user_data["count_photo"])):
                        await bot.send_photo(person_id,
                                             rapid_hotels_api.get_photo(return_info[index]["id"])["hotelImages"][i][
                                                 "baseUrl"].format(
                                                 size="z"
                                             ))
        except (IndexError, KeyError, TypeError) as exc:
            await state.finish()
            await message.answer('Это все, что нам удалось найти!')
            logger.error(f"Возникла ошибка: {exc}")
        await state.finish()
        sql.add_history(person_id, history_dict)
    else:
        await message.answer('Введите цифрами!')


def register_high_price(dp: Dispatcher):
    """
    Регистрация handlers
    :param dp: Dispatcher
    :return: None
    """
    dp.register_callback_query_handler(started_high_price, text='button1')
    dp.register_message_handler(started_high_price_2, commands=['high_price'])
    dp.register_message_handler(waite_city_state_2, state=WaiteCityAndCount2.waite_city_state2)
    dp.register_callback_query_handler(waite_photo_state_2, state=WaiteCityAndCount2.waite_photo_answer2)
    dp.register_message_handler(waite_count_photo_state_2, state=WaiteCityAndCount2.waite_photo_count2)
    dp.register_message_handler(watch_hotels_2, state=WaiteCityAndCount2.waite_count_state2)
    dp.register_message_handler(waite_date, state=WaiteCityAndCount2.waite_date_state2)