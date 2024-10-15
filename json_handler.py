import json
from datetime import datetime
from typing import List, Dict, Tuple
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_JSON_FILE_NAME = os.getenv('news_json_file_name')
PLOT_DATA_JSON_FILE_NAME = os.getenv('plot_data_json_file_name')


def read_json_file(file_name: str) -> dict:
    """
    Чтение JSON файла
    :param file_name: Имя файла
    :return: Словарь с данными, прочитанными из JSON файла
    """
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def write_json_file(file_name: str, data: dict) -> None:
    """
    Запись данных в JSON файл
    :param file_name: Имя файла для записи данных
    :param data: Данные, которые будут записаны в файл в формате JSON
    :return: None
    """
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def parse_date(news_item: dict) -> datetime:
    """
    Парсинг даты из строки формата DD.MM.YYYY
    :param news_item: Словарь с новостным элементом, содержащим строку даты
    :return: Объект datetime, представляющий дату новости
    """
    return datetime.strptime(news_item['date'], "%d.%m.%Y")


def sort_by_date(news_data: List[dict], ascending: bool) -> List[dict]:
    """
    Сортировка списка новостей по дате
    :param news_data: Список новостных элементов для сортировки
    :param ascending: Флаг сортировки. Если True, сортировка по возрастанию; если False — по убыванию
    :return: Отсортированный список новостных элементов
    """
    return sorted(news_data, key=parse_date, reverse=not ascending)


def get_texts(ascending: bool = True) -> Tuple[List[str], List[str]]:
    """
    :param ascending: Флаг сортировки. Если True, сортировка по возрастанию; если False — по убыванию
    :return: тексты и даты новостей в отсортированном порядке
    """
    news_data = read_json_file(NEWS_JSON_FILE_NAME)
    sorted_news = sort_by_date(news_data, ascending)
    texts = [f"{item['title']}. {item['text']}".strip() for item in sorted_news]
    dates = [item['date'] for item in sorted_news]
    return texts, dates


def get_news_data(ascending: bool = True) -> List[Dict[str, str]]:
    """
    :param ascending: Флаг сортировки. Если True, сортировка по возрастанию; если False — по убыванию
    :return: Список словарей, где каждый словарь содержит информацию о новости (заголовок, текст, дата, ссылка)
    """
    news_data = read_json_file(NEWS_JSON_FILE_NAME)
    return sort_by_date(news_data, ascending)


def get_titles(ascending: bool = True) -> List[str]:
    """
    :param ascending: Флаг сортировки. Если True, сортировка по возрастанию; если False — по убыванию
    :return: Список строк, содержащий заголовки новостей
    """
    news_data = get_news_data(ascending)
    return [news_item['title'] for news_item in news_data]


def get_plot_data() -> dict:
    """
    :return: Словарь, содержащий данные для построения графиков
    """
    return read_json_file(PLOT_DATA_JSON_FILE_NAME)


def update_plot_data(new_data: dict) -> None:
    """
    Обновление данных для графика
    :param new_data: Словарь с новыми данными для обновления (предсказания, даты и заголовки)
    :return: None
    """
    plot_data = get_plot_data()
    for key in ['predictions', 'dates', 'titles']:
        plot_data.setdefault(key, []).append(new_data.get(key))
    write_json_file(PLOT_DATA_JSON_FILE_NAME, plot_data)


def remove_plot_data() -> None:
    """
    Удаление последних данных для графика (последний элемент каждого списка — predictions, dates и titles)
    :return: None
    """
    plot_data = get_plot_data()
    for key in ['predictions', 'dates', 'titles']:
        if plot_data.get(key):
            plot_data[key].pop()
    write_json_file(PLOT_DATA_JSON_FILE_NAME, plot_data)


def save_plot_data(predictions, dates, titles):
    """
    Сохраняет данные предсказаний, дат и заголовков новостей в JSON файл.

    :param predictions: Список предсказанных значений (выходов модели).
    :param dates: Список дат, связанных с предсказаниями.
    :param titles: Список заголовков новостей, соответствующих предсказаниям.
    :return: None
    """
    plot_data = {
        'predictions': predictions,
        'dates': dates,
        'titles': titles
    }
    with open(PLOT_DATA_JSON_FILE_NAME, 'w', encoding='utf-8') as json_file:
        json.dump(plot_data, json_file, ensure_ascii=False, indent=4)