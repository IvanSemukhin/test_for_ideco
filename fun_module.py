# fun_module.py
# вспомогательные функции.

from config import *
import json
import datetime


def get_json_data(path):
    """
    читает json данные из файла.
    :param path: путь к файлу.
    :return: json данные в виде словаря.
    """
    with open(path, 'r') as source_file:
        return json.load(source_file)


def get_all_data():
    """
    читает все данные необходимые для задачи.
    :return: кортеж из двух json словарей.
    """
    js_dic_news = get_json_data(NEWS)
    js_dic_comments = get_json_data(COMMENTS)
    return js_dic_news, js_dic_comments


def get_now():
    """
    получает текущее время.
    :return: Объект datetime с текущим временем.
    """
    return datetime.datetime.fromisoformat(datetime.datetime.now().isoformat(timespec='seconds'))


def get_datetime(time_string):
    """
    возвращает объект datetime из входной строки формата ISO 8601.
    :param time_string: строка формата ISO 8601.
    :return: объект datetime.
    """
    return datetime.datetime.fromisoformat(time_string)


def is_early(new, time):
    """
    проверяет, что время новости ещё не настало.
    :param new: новость со всеми её параметрами (на уровне python это словарь).
    :param time: текущее время.
    :return: True, если время новости ещё не наступило, False в противном случае.
    """
    return get_datetime(new[KEY_NEW_DATE]) > time


def check_comment_time_by_new(new, comment):
    """
    проверяет позднее ли время коментария времени новости.
    :param new: новость со всеми её параметрами (на уровне python это словарь).
    :param comment: комментарий со всеми её параметрами (на уровне python это словарь).
    :return: True, если время новости меньше времени комментария, False в противном случае.
    """
    return get_datetime(new[KEY_NEW_DATE]) < get_datetime(comment[KEY_COMMENT_DATE])


def error_time(new, comment):
    """
    функция для информирования о несоответсвии времени. Просто печатает в консоль оба словаря.
    :param new: новость со всеми её параметрами (на уровне python это словарь).
    :param comment: коммунтарий со всеми её параметрами (на уровне python это словарь).
    :return: None
    """
    print("комментарий:", comment)
    print("не может быть раньше новости", new)


def filter_news(dic, time):
    """
    фильтрует список новостей в json словаре. с помощью временного списка,
    удаляет новости с полем deleted = True и время, которых ещё не настало.
    :param dic: json словарь из файла.
    :param time: текущее время.
    :return: None
    """
    tmp_lst = dic[KEY_NEWS].copy()
    for el in tmp_lst:
        if el[KEY_DELETED] or is_early(el, time):
            dic[KEY_NEWS].remove(el)


def merge_news_comments(dic_news, dic_comments):
    """
    подсчитывает кол-во комментариев к новостям. Использует поле для проверки 'news_id'.
    проверяет время комментария.
    :param dic_news: json словарь из файла новостей.
    :param dic_comments: json словарь из файла комментариев.
    :return: None
    """
    for new in dic_news[KEY_NEWS]:
        new.setdefault(KEY_COMMENTS_COUNT, 0)
        for comment in dic_comments[KEY_COMMENTS]:
            if comment[KEY_NEWS_ID] == new[KEY_ID]:
                if check_comment_time_by_new(new, comment):
                    new[KEY_COMMENTS_COUNT] += 1
                else:
                    error_time(new, comment)


def search(dic_news, new_id):
    """
    линейный поиск по id новости.
    :param dic_news: json словарь из файла новостей.
    :param new_id: id новости.
    :return: dict - словарь(новость) с ключами и значениями найденой новости, если найдена, None в противном случае
    """
    for el in dic_news[KEY_NEWS]:
        if el[KEY_ID] == new_id:
            return el
    return None


def check_new(new, time):
    """
    проверяет новость на годность по времени и флаг удаления.
    :param new: новость со всеми её параметрами (на уровне python это словарь).
    :param time: текущее время запроса.
    :return: True, если время новости настало и она не удалена, False в противном случае.
    """
    return get_datetime(new[KEY_NEW_DATE]) < time and not new[KEY_DELETED]


def add_comments(new, dic_comments):
    """
    присоединяет коментарии к новости по полю 'news_id'.
    :param new: новость со всеми её параметрами (на уровне python это словарь).
    :param dic_comments: json словарь из файла комментариев.
    :return: None
    """
    new.setdefault(KEY_COMMENTS, [])
    new.setdefault(KEY_COMMENTS_COUNT, 0)

    for comment in dic_comments[KEY_COMMENTS]:
        if new[KEY_ID] == comment[KEY_NEWS_ID]:
            if check_comment_time_by_new(new, comment):
                new[KEY_COMMENTS].append(comment)
                new[KEY_COMMENTS_COUNT] += 1
            else:
                error_time(new, comment)

    new[KEY_COMMENTS].sort(key=lambda el: get_datetime(el[KEY_COMMENT_DATE]))
