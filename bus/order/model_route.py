from dataclasses import dataclass
from database.select import select_dict1, insert_many, insert,select_list1
from flask import session, current_app
from cache.wrapper import fetch_from_cache

@dataclass
class ResultInfo:
    result: tuple
    status: bool
    err_message: str

def model_route_select(provider, user_input: dict, sql_file: str):
    err_message = ""
    _sql = provider.get(sql_file)
    result = select_dict1(_sql, user_input)
    if result:
        return ResultInfo(result=result, status=True, err_message=err_message)
    else:
        return ResultInfo(result=result, status=False, err_message="DATA NOT FOUND")

def model_route(provider, user_input: dict, sql_file: str,cache_name:str):
    cache_config = current_app.config['cache_config']
    cache_select = fetch_from_cache(cache_name, cache_config)(select_dict1)
    err_message = ""
    _sql = provider.get(sql_file)
    result = cache_select(_sql, user_input)
    if result:
        return ResultInfo(result=result, status=True, err_message=err_message)
    else:
        return ResultInfo(result=result, status=False, err_message="DATA NOT FOUND")

def model_route_add(provider, user_input: dict, sql_file: str):
    _sql = provider.get(sql_file)
    if user_input['action'] == 'Удалить':
        d_id = user_input['D_ID']
        if 'basket' in session and d_id in session['basket']:
            session['basket'].pop(d_id)
            session.modified = True
        return True
    else:
        user_dict = {'D_ID': user_input['D_ID']}
        result = select_dict1(_sql, user_dict)
        object_id = user_input['R_ID']
        if result:
            add_to_basket(result[0],object_id)
            return True
        else:
            return False

def add_to_basket(driver: dict,object_id:str):
    if 'basket' not in session:
        session['basket'] = {}
    d_id = str(driver['D_ID'])
    session['basket'][d_id] = {'D_ID': d_id, 'D_NAME': driver['D_NAME'],'R_ID': object_id}
    session.modified = True
    return True

def model_route_insert(provider, sql_file1: str):
    _sql1 = provider.get(sql_file1)
    result = insert_many(_sql1)
    if result:
        return result
    return False

def model_route_show(provider, sql_file: str):
    err_message = ""
    user_list = [session.get('date')]
    _sql = provider.get(sql_file)
    print("sql=", _sql)
    result, schema = select_list1(_sql, user_list)
    print("result=", result)
    print("schema=", schema)
    if result:
        return ResultInfo(result=result, status=True, err_message=err_message), schema
    else:
        return ResultInfo(result=result, status=False, err_message="DATA NOT FOUND"), schema