import requests
import json
from loguru import logger
from fuzzywuzzy import process
from config import headers, url, url_2, url_3, cities


class Parsing:
    def __init__(self, used_url: str, querystring: dict, used_headers: dict) -> None:
        """
        :param used_url: str
        :param querystring: dict
        :param used_headers: dict
        """
        self.used_url = used_url
        self.querystring = querystring
        self.used_headers = used_headers

    def get_id(self) -> dict:
        """
        Делаем запрос, возвращаем ID
        нужного нам города
        :return: dict
        """

        try:
            response = requests.request("GET", self.used_url, headers=self.used_headers, params=self.querystring, timeout=10)
            data = json.loads(response.text)
            with open('data_id.json', 'w') as file_1:
                json.dump(data, file_1, indent=4)
            return data["suggestions"][0]["entities"][0]["destinationId"]
        except (ConnectionError, TimeoutError) as exc:
            logger.error('Возникла ошибка:', exc)


class GetInformation(Parsing):

    def get_information(self) -> dict:
        """
        Делаем запрос и возвращаем все найденные отели,
        используя ID города
        :return: dict
        """

        try:
            response = requests.request("GET", self.used_url, headers=self.used_headers, params=self.querystring, timeout=10)
            if response.status_code == requests.codes.ok:
                data = json.loads(response.text)
                with open('data.json', 'w') as file:
                    json.dump(data, file, indent=4)
                return data
        except (ConnectionError, TimeoutError) as exc:
            logger.error('Возникла ошибка:', exc)


class GetHotelsPhoto(Parsing):

    def get_hotels_photo(self) -> dict:
        """
        Делаем запрос и
        возвращаем фотографии, используя ID отеля
        :return: dict
        """

        try:
            response = requests.request("GET", self.used_url, headers=self.used_headers, params=self.querystring, timeout=10)
            if response.status_code == requests.codes.ok:
                data = json.loads(response.text)
                return data
        except (ConnectionError, TimeoutError) as exc:
            logger.error('Возникла ошибка:', exc)


def get_id(city: str, setting: str) -> tuple:
    """
    Создаем объекты классов, передаем параметры,
    которые были введены пользователем
    :param city:
    :param setting:
    :return: tuple
    """
    real_city = process.extract(city, cities, limit=1)
    logger.info(f'Совпадения и его %: {real_city}')

    if real_city[0][1] > 70:
        city = real_city[0][0]

    logger.info(f'Исправленный город: {city}')
    querystring = {"query": f"{real_city[0][0]}", "locale": "ru_RUS", "currency": "RUB"}
    pars = Parsing(used_url=url, querystring=querystring, used_headers=headers)

    city_id = pars.get_id()

    querystring_2 = {
        "destinationId": f"{city_id}", "pageNumber": "1", "pageSize": "25", "checkIn": "2020-01-08",
        "checkOut": "2020-01-15", "adults1": "1", "sortOrder": f"{setting}", "locale": "ru_RUS", "currency": "RUB"}

    get_info = GetInformation(used_url=url_2, querystring=querystring_2, used_headers=headers)

    return get_info.get_information(), real_city[0][0]


def get_photo(hotel_id: str) -> dict:
    """
    Создаем объект класса,
    возвращаем пользователю фотографии отелей
    :param hotel_id: str
    :return: dict
    """
    querystring = {"id": f"{hotel_id}"}
    get_hotels_photo = GetHotelsPhoto(used_url=url_3, querystring=querystring, used_headers=headers)

    return get_hotels_photo.get_hotels_photo()
