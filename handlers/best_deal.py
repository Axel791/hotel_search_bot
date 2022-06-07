import re

from config import path
from keyboards import keyboards
from aiogram import types, Dispatcher
from aiogram.utils.markdown import hbold
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from utils import rapid_hotels_api
from time import sleep
from database import sqlite
from loader import bot
from loguru import logger

sql = sqlite.Sqlite(path)


class WaiteCity(StatesGroup):
    """
    Создаем состояния
    """
    waite_city = State()
    waite_distance_to_the_center = State()
    waite_cost = State()
    waite_photo = State()
    waite_count_photo = State()
    waite_date_state = State()
    waite_count = State()


async def started_best_deal(callback_query: types.CallbackQuery):
    """
    Активация best_deal через
    инлайн клавиатуру
    :param callback_query: types.CallbackQuery
    :return: None
    """
    await callback_query.message.edit_text('Напишите название города🏢: ')
    await callback_query.message.edit_reply_markup(reply_markup=keyboards.inline_buttons_3)
    await WaiteCity.waite_city.set()


async def started_best_deal_2(message: types.Message):
    """
    Активация best_deal через
    команду /best_deal
    :param message: types.Message
    :return: None
    """
    await message.answer('Напишите название города🏢: ')
    await WaiteCity.waite_city.set()


async def chose_distance(message: types.Message, state: FSMContext):
    """
    Пользователь вводит
    дистанцию до центра
    сохраняем город в словарь и
    проверяем его корректность
    :param message: types.Message
    :param state: FSMContext
    :return: None
    """

    if not message.text.isdigit():
        logger.info(f'Город:{message.text}')
        await message.answer(f'Напишите желаемый диапазон расстояния до центра:\n'
                             f'{hbold("Пример написания: 0,3-1,5 или 0.4-1.6")}', reply_markup=keyboards.inline_buttons_4)
        await state.update_data(city=message.text)
        await WaiteCity.waite_distance_to_the_center.set()
    else:
        await message.answer('Напишите название города буквами!')


async def chose_cost(message: types.Message, state: FSMContext):
    """
    Получаем желаемое расстояние до центра,
    проверяем его на корректность,
    запрашиваем у человека диапазон цен за ночь(в рублях),
    расстояние сохраняем в словарь
    :param message: types.Message
    :param state: FSMContext
    :return: None
    """

    logger.info(f'Дистанция:{message.text}')
    distant = re.findall(r"[0-9]*[.]*[,]?[0-9]+", message.text)
    dist_list = [num.replace(",", ".") for num in distant]
    if (len(dist_list) == 2) and not (all(i.isalpha() for i in dist_list)) and (dist_list is not None):
        await message.answer(f'Напишите желаемый диапазон цен за ночь(в рублях):\n'
                             f'{hbold("Пример написания: 1000-1500")}', reply_markup=keyboards.inline_buttons_4)
        await state.update_data(distance=dist_list)
        await WaiteCity.waite_cost.set()
    else:
        await message.answer('Введите дистанцию как в примере!')


async def chose_count(message: types.Message, state: FSMContext):
    """
    Получаем желаемый диапазон цен за ночь(в рублях),
    проверяем его на корректность,
    запрашиваем у человека ответ на вопрос о фотографиях,
    переходим к следующему состоянию в зависимости от ответа
    :param message: types.Message
    :param state: FSMContext
    :return: None
    """
    logger.info(f'Диапазон цен:{message.text}')
    price_list = re.findall(r"\d+", message.text)
    if len(price_list) == 2 and price_list is not None:
        await message.answer('Вам показать фотографии найденных отелей ?', reply_markup=keyboards.inline_buttons_2)
        await state.update_data(cost=price_list)
        await WaiteCity.waite_photo.set()
    else:
        await message.answer('Введите диапазон цен как в примере!')


async def waite_photo_answer(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Принимаем ответ пользователя о фотографиях,
    переходим к следующему состоянию
    :param callback_query: types.CallbackQuery
    :param state: FSMContext
    :return: None
    """
    await callback_query.message.edit_reply_markup()
    photo_data = callback_query.data
    logger.info(f'Ответ пользователя:{callback_query.data}')
    await state.update_data(photo=photo_data)
    if photo_data == 'yes':
        await callback_query.message.answer("Сколько фото вам показать?", reply_markup=keyboards.inline_buttons_4)
        await WaiteCity.waite_count_photo.set()
    else:
        await WaiteCity.waite_date_state.set()
        await callback_query.message.answer('Введите дату заселения и дату выезда как в примере'
                                            f'{hbold("ДД.ММ.ГГ-ДД.ММ.ГГ")}', reply_markup=keyboards.inline_buttons_4)


async def waite_count_photo(message: types.Message,  state: FSMContext):
    """
    Запрашиваем у пользователя кол-во отелей,
    записываем все данные в словарь
    :param message: types.Message
    :param state: FSMContext
    :return: None
    """

    if message.text.isdigit():
        logger.info(f'Кол-во фото:{message.text}')
        await message.answer('Сколько отелей вам показать?', reply_markup=keyboards.inline_buttons_4)
        await state.update_data(count_photo=message.text)
        await WaiteCity.waite_date_state.set()


async def waite_date_2(message: types.Message, state: FSMContext):
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
        await WaiteCity.waite_count.set()
    else:
        await message.answer('Дата введена некорректно!')


async def waite_city(message: types.Message, state: FSMContext):
    """
    Отправляем пользователю, что удалось найти по его данным,
    записываем найденные отели в БД, для просмотра истории
    :param message: types.Message
    :param state: FSMContext
    :return: None
    """
    person_id = message.from_user.id
    if message.text.isdigit():
        logger.info(f'Кол-во отелей:{message.text}')
        await message.answer('Идет поиск, подождите пару секунд...⌛️', reply_markup=keyboards.keyboard)
        await state.update_data(count=message.text)
        user_data = await state.get_data()
        history_dict = {"city": None, "search_results": []}
        counter = 0
        try:
            full_info = rapid_hotels_api.get_id(user_data["city"], "PRICE_HIGHEST_FIRST")
            return_info = full_info[0]["data"]["body"]["searchResults"]["results"]
            history_dict["city"] = full_info[1]
            for index in range(0, 26):
                dist = float(return_info[index]["landmarks"][0]["distance"][:3].replace(',', '.'))
                if (float(user_data["distance"][0]) <= dist <= float(user_data["distance"][1]) and
                        int(user_data["cost"][0]) <= return_info[index]["ratePlan"]["price"]["exactCurrent"]
                        <= int(user_data["cost"][1])):
                    sleep(0.1)
                    if counter != int(user_data["count"]):
                        price = (((int(user_data["date"][0]) + int(user_data["date"][3])) +
                                  (30 * (int(user_data["date"][4]) - int(user_data["date"][1]))))
                                 * return_info[index]["ratePlan"]["price"]["exactCurrent"])
                        answer = (f'{hbold(return_info[index]["name"])}'
                                  f'\n\nАдрес:  {return_info[index]["address"]["streetAddress"]}'
                                  f'\nРасстояние до центра:  {return_info[index]["landmarks"][0]["distance"]}'
                                  f'\nРейтинг:  {return_info[index]["starRating"]}'
                                  f'\nЦена:  {round(price, 3)} RUB')
                        await message.answer(answer)
                        if user_data["photo"] == 'yes':
                            for index_2 in range(0, int(user_data["count_photo"])):
                                await bot.send_photo(person_id, rapid_hotels_api.get_photo
                                (return_info[index]["id"])["hotelImages"][index_2]["baseUrl"].format(
                                    size="z"
                                ))
                        history_dict["search_results"].append(answer)
                        counter += 1
                    else:
                        break
        except (IndexError, KeyError) as exc:
            await state.finish()
            await message.answer('Это все отели, которые нам удалось подобрать по данным, которые вы указали.')
            logger.error(f"Возникла ошибка:{exc}")
        await state.finish()
        sql.add_history(person_id, history_dict)
    else:
        await message.answer('Введите число отелей цифрами!')


async def forming_cancel_button_on_state(callback_query: types.CallbackQuery, state: FSMContext):
    """
    Кнопка отмены, сброс всех состояний
    :param callback_query: types.CallbackQuery
    :param state: FSMContext
    :return: None
    """
    await state.finish()
    await callback_query.message.edit_reply_markup()
    await callback_query.message.answer('Действие отменено!Поиск прекращён...✖')


def register_best_deal_handlers(dp: Dispatcher):
    """
    Регистрируем хэндлеры
    :param dp: Dispatcher
    :return: None
    """
    dp.register_message_handler(started_best_deal_2, commands=['best_deal'])
    dp.register_callback_query_handler(waite_photo_answer, state=WaiteCity.waite_photo)
    dp.register_callback_query_handler(started_best_deal, text='button3')
    dp.register_message_handler(waite_count_photo, state=WaiteCity.waite_count_photo)
    dp.register_message_handler(chose_distance, state=WaiteCity.waite_city)
    dp.register_message_handler(chose_cost, state=WaiteCity.waite_distance_to_the_center)
    dp.register_message_handler(chose_count, state=WaiteCity.waite_cost)
    dp.register_message_handler(waite_city, state=WaiteCity.waite_count)
    dp.register_callback_query_handler(forming_cancel_button_on_state, text="cancel",  state="*")
    dp.register_message_handler(waite_date_2, state=WaiteCity.waite_date_state)