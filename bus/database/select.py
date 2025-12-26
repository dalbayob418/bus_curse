# Описываем действия, выполняющиеся при запросе
from database.DBcm import DBContextManager
from flask import current_app,session # Позволяет обратится к глобальным переменным
from datetime import date

def select_list(_sql: str, param_list: list) -> set: # Возвращает кортеж кортежей
    with DBContextManager(current_app.config['db_config']) as cursor:
        if cursor is None:
            raise ValueError('Не удалось подключиться')
        else:
            cursor.execute(_sql, param_list)
            result = cursor.fetchall()
            return result

def select_dict(_sql: str, user_input: dict) -> tuple:
    user_list = []
    for key in user_input:
        user_list.append(user_input[key])
    print('user_list={} in dict'.format(user_list))
    result = select_list(_sql, user_list)
    return result

def select_list1(_sql: str, user_list: list):
    with DBContextManager(current_app.config['db_config']) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        else:
            cursor.execute(_sql, user_list)
            result = cursor.fetchall()
            schema = []
            for item in cursor.description:
                schema.append(item[0])
    return result, schema

def select_dict1(_sql, user_dict: dict):
    user_list = list(user_dict.values())
    result, schema = select_list1(_sql, user_list)
    result_dict = []
    for item in result:
        result_dict.append(dict(zip(schema, item)))
    return result_dict

def stored_proc(proc_name: str, rep_date: list):
    msg=''
    with DBContextManager(current_app.config['db_config']) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        else:
            cursor.callproc(proc_name, rep_date)
            msg = cursor.fetchall()
    return msg

def insert_many(_sql1: str):
    with DBContextManager(current_app.config['db_config']) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        else:
            basket = session.get('basket')
            for key, item in basket.items():
                user_dict = {'date': date.fromisoformat(session.get('date')), 'D_ID': int(item['D_ID']),'R_ID': int(item['R_ID'])}
                print(user_dict)
                cursor.execute(_sql1, user_dict)
            if cursor.rowcount == 0:
                raise ValueError('Insert не выполнен')
            last_inserted=cursor.lastrowid
    return last_inserted

def insert(_sql: str, user_dict: dict):
    with DBContextManager(current_app.config['db_config']) as cursor:
        if cursor is None:
            raise ValueError('Курсор не создан')
        else:
            cursor.execute(_sql, user_dict)
            if cursor.rowcount == 0:
                raise ValueError('Insert не выполнен')
            last_inserted = cursor.lastrowid
    return last_inserted