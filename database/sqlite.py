import sqlite3
from loguru import logger


class Sqlite:

    def __init__(self, db_file: str) -> None:
        """
        Подключаемся к БД
        :param db_file:
        """

        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()

    def add_user(self, user_id: str) -> None:
        """
        Проверяем пользователя на наличие
        его в базе данных,
        если нет, то заполняем ее
        :param user_id:
        :return: None
        """

        txt = None
        check_user = self.cursor.execute("SELECT * FROM city_history WHERE user_id=?", (user_id, ))
        if check_user.fetchone() is None:
            self.cursor.execute("INSERT INTO city_history VALUES(?, ?, ?, ?, ?, ?, ?)", (user_id, txt, txt, txt, txt, txt, txt))
            self.conn.commit()
            logger.info(f'Новый пользователь{user_id}')
        else:
            logger.info('Пользователь есть в БД')

    def add_history(self, user_id: int, info: dict) -> None:
        """
        Добавляем новый запрос в историю
        пользователя со сдвигом на 1
        :param user_id: int
        :param info: dict
        :return: None
        """

        city1 = self.cursor.execute("SELECT first_search FROM city_history WHERE user_id=?", (user_id, ))
        city2 = self.cursor.execute("SELECT second_search FROM city_history WHERE user_id=?", (user_id,))
        city3 = self.cursor.execute("SELECT third_search FROM city_history WHERE user_id=?", (user_id,))

        if info["search_results"] is not None:
            string = ''
            for i_elem in info["search_results"]:
                string += i_elem + ' '

        else:
            string = 'История поиска этого города пуста.'

        if city1 is None and city2 is None and city3 is None:
            self.cursor.execute("UPDATE city_history SET first_search=? WHERE user_id=?", (string, user_id))
            self.cursor.execute("UPDATE city_history SET first_city=? WHERE user_id=?", (info["city"], user_id))
            self.conn.commit()

        elif city1 is not None and city2 is None and city3 is None:
            self.cursor.execute("UPDATE city_history SET second_search=first_search WHERE user_id=?", (user_id, ))
            self.cursor.execute("UPDATE city_history SET second_city=first_city WHERE user_id=?", (user_id, ))
            self.cursor.execute("UPDATE city_history SET first_search=? WHERE user_id=?", (string, user_id))
            self.cursor.execute("UPDATE city_history SET first_city=? WHERE user_id=?", (info["city"], user_id))
            self.conn.commit()

        else:
            self.cursor.execute("UPDATE city_history SET third_search=second_search WHERE user_id=?", (user_id,))
            self.cursor.execute("UPDATE city_history SET third_city=second_city WHERE user_id=?", (user_id,))
            self.cursor.execute("UPDATE city_history SET second_search=first_search WHERE user_id=?", (user_id, ))
            self.cursor.execute("UPDATE city_history SET second_city=first_city WHERE user_id=?", (user_id,))
            self.cursor.execute("UPDATE city_history SET first_search=? WHERE user_id=?", (string, user_id))
            self.cursor.execute("UPDATE city_history SET first_city=? WHERE user_id=?", (info["city"], user_id))
            self.conn.commit()

        logger.info(f"Новая запись в истории {user_id}|{info['city']}")

    def return_city(self, user_id: int) -> tuple:
        """
        Возвращаем города из
        истории поиска для
        дальнейшей работы с ними
        :param user_id: int
        :return: tuple
        """

        city_1 = self.cursor.execute("SELECT first_city FROM city_history WHERE user_id=?", (user_id, )).fetchone()[0]
        city_2 = self.cursor.execute("SELECT second_city FROM city_history WHERE user_id=?", (user_id,)).fetchone()[0]
        city_3 = self.cursor.execute("SELECT third_city FROM city_history WHERE user_id=?", (user_id,)).fetchone()[0]
        return city_1, city_2, city_3

    def return_first_city_history(self, user_id: int) -> str:
        """
        Возвращаем историю запроса
        первого города пользователю
        :param user_id: int
        :return: str
        """

        f_city = self.cursor.execute("SELECT first_search FROM city_history WHERE user_id=?", (user_id, )).fetchone()[0]
        return f_city

    def return_second_city_history(self, user_id: int) -> str:
        """
        Возвращаем историю запроса
        второго города пользователю
        :param user_id: int
        :return: str
        """

        s_city = self.cursor.execute("SELECT second_search FROM city_history WHERE user_id=?", (user_id, )).fetchone()[0]
        return s_city

    def return_third_city_history(self, user_id: str) -> str:
        """
        Возвращаем историю запроса
        третьего города пользователю
        :param user_id: int
        :return: str
        """

        t_city = self.cursor.execute("SELECT third_search FROM city_history WHERE user_id=?", (user_id, )).fetchone()[0]
        return t_city
