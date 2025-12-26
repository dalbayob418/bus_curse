import os
from flask import Blueprint, render_template, request, session, redirect, url_for
from order.model_route import model_route, model_route_add, model_route_insert,model_route_select,model_route_show
from database.sql_provider import SQLProvider
from access import group_required

blueprint_order = Blueprint(
    'blueprint_order',
    __name__,
    template_folder='templates'
)

provider = SQLProvider(os.path.join(os.path.dirname(__file__), 'sql'))

@blueprint_order.route('/date', methods=["GET","POST"])
@group_required
def date_index():
    if request.method == "POST":
        user_input = request.form
        print(user_input['date'])
        result_info = model_route_select(provider, user_input, 'date.sql')
        if result_info.status:
            return render_template('date_exists.html', date=user_input['date'])
        else:
            session['date'] = user_input['date']
            return redirect(url_for('blueprint_order.order_index'))
    else:
        return render_template("date.html")

@blueprint_order.route('/', methods=["GET"])
@group_required
def order_index():
    if 'date' not in session:
        return redirect(url_for('blueprint_order.date_index'))
    user_input={}
    result_info = model_route(provider, user_input , 'drivers.sql','drivers')
    items = result_info.result
    routes = model_route(provider, {}, 'routes.sql','routes').result
    basket=session.get('basket')
    count=count2=0
    for item in items:
        item['free'] = 0
        count += 1
    if basket:
        for item in items:
            if str(item['D_ID']) in basket:
                item['free'] = 1
                count2+=1
                count-=1
    session['count'] = count
    return render_template("basket_order_list.html", items=items, basket=basket,routes=routes,count=count,count2=count2)

@blueprint_order.route('/add', methods=["POST"])
@group_required
def add_index():
    user_input=request.form
    result_status = model_route_add(provider, user_input, 'driver.sql')
    if result_status:
        return redirect(url_for('blueprint_order.order_index'))
    else:
        return render_template("basket_err.html",error="добавлении водителя в расписание")

@blueprint_order.route('/clear', methods=["GET"])
@group_required
def clear_basket():
    if 'basket' in session:
        session.pop('basket')
    return redirect(url_for('blueprint_order.order_index'))

@blueprint_order.route('/save', methods=["GET"])
@group_required
def save_schedule():
    if 'basket' in session and session['count'] == 0:
        res_insert = model_route_insert(provider, 'insert.sql')
        if res_insert:
            session.pop('basket')
            results,schema = model_route_show(provider, 'show.sql')
            date=session.get('date')
            session.pop('date')
            session.modified = True
            return render_template("schedule_saved.html",results=results.result,date=date)
        else:
            return render_template("basket_err.html",error="формировании расписания")
    else:
        return redirect(url_for('blueprint_order.order_index'))

@blueprint_order.route('/exit', methods=["GET"])
@group_required
def exit():
    if 'count' in session:
        session.pop('count')
    if 'date' in session:
        session.pop('date')
    if 'basket' in session:
        session.pop('basket')
    return redirect('/')