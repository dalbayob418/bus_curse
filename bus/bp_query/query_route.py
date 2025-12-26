# bp_query/query_route.py
import os
from flask import Blueprint, render_template, request, current_app

from access import login_required, group_required
from database.sql_provider import SQLProvider   # ← правильный импорт
from database.select import select_list
from database.DBcm import DBContextManager

blueprint_query = Blueprint('bp_query', __name__, template_folder='templates')
provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

# Словарь русских заголовков для каждого запроса
RUS_HEADERS = {
    'driver_by_name.sql': {
        'D_ID': 'ID водителя',
        'D_NAME': 'ФИО',
        'D_BIRTH': 'Дата рождения',
        'D_ADRESS': 'Адрес',
        'D_DATA_OF_REC': 'Дата приёма на работу',
        'D_DATA_OF_DISM': 'Дата увольнения'
    },
    'trolley_by_number.sql': {
        'T_ID': 'ID записи',
        'T_DATE': 'Дата',
        'T_ENTRY_DATE': 'Время входа',
        'T_EXIT_DATE': 'Время выхода',
        'T_TROLL_NUMBER': 'Бортовой номер',
        'driver_name': 'ФИО водителя',
        'route_name': 'Название маршрута'
    },
    'drivers_by_recruitment_year.sql': {
        'D_ID': 'ID',
        'D_NAME': 'ФИО',
        'D_BIRTH': 'Дата рождения',
        'D_ADRESS': 'Адрес',
        'D_DATA_OF_REC': 'Дата приёма',
        'D_DATA_OF_DISM': 'Дата увольнения'
    }
}

@blueprint_query.route('/', methods=['GET'])
@login_required
@group_required
def product_handle():
    return render_template('query_menu.html')


@blueprint_query.route('/form/<sql_file>', methods=['GET'])
@login_required
@group_required
def query_form(sql_file):
    titles = {
        'driver_by_name.sql': 'Поиск водителя по части ФИО',
        'trolley_by_number.sql': 'Поиск троллейбуса по бортовому номеру',
        'drivers_by_recruitment_year.sql': 'Водители, принятые в указанном году'
    }
    placeholders = {
        'driver_by_name.sql': 'Например: Иванов',
        'trolley_by_number.sql': 'Введите бортовой номер',
        'drivers_by_recruitment_year.sql': 'Год (например: 2020)'
    }

    return render_template('query_form.html',
                           title=titles.get(sql_file, 'Запрос'),
                           placeholder=placeholders.get(sql_file, ''),
                           sql_file=sql_file)


@blueprint_query.route('/result', methods=['POST'])
@login_required
@group_required
def query_result():
    sql_file = request.form.get('sql_file')
    param = request.form.get('param', '').strip()

    if not sql_file or not param:
        return "Ошибка: не передан параметр", 400

    sql = provider.get(sql_file)

    # Для поиска по ФИО автоматически добавляем %
    if sql_file == 'driver_by_name.sql':
        param = f"%{param}%"

    # Выполняем запрос
    result = select_list(sql, [param])

    if not result:
        return render_template('dynamic.html', title="Результат", columns=[], items=[])

    # Получаем оригинальные имена колонок
    db_config = current_app.config['db_config']
    with DBContextManager(db_config) as cursor:
        cursor.execute(sql, [param])
        orig_columns = [desc[0] for desc in cursor.description]

    # Заменяем на русские, если есть в словаре
    columns = []
    for col in orig_columns:
        columns.append(RUS_HEADERS.get(sql_file, {}).get(col, col))

    return render_template('dynamic.html',
                           title="Результат запроса",
                           columns=columns,
                           items=result)