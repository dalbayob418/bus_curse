from dataclasses import dataclass
from database.select import select_dict


@dataclass
class ResultInfo:
    result: tuple
    status: bool
    err_message: str = ''


def model_route(provider, user_input: dict):
    filename = user_input.get('sql_file')
    if not filename:
        return ResultInfo((), False, "SQL-файл не указан")

    _sql = provider.get(filename)
    if not _sql:
        return ResultInfo((), False, "SQL-запрос не найден")

    params_for_db = {k: v for k, v in user_input.items() if k != 'sql_file'}

    try:
        result = select_dict(_sql, params_for_db)
        return ResultInfo(result, bool(result), '' if result else 'Нет данных')
    except Exception as e:
        return ResultInfo((), False, f"Ошибка БД: {e}")