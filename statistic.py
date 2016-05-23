from datetime import datetime, timedelta

from models import OrderMenu, Order, Menu
from mydb import db_session as db


# in 기간, 메뉴리스트, 단위 out 단위에 맞춰서 각 메뉴별 총액 및 개수
# unit : 1. 시간, 2. 일, 3. 요일, 4. 월, 5. 분기, 6. 년
def increaseTotalPrice(ordermenu, dic):
    if ordermenu.pay == 1:
        if "cashtotal" in dic:
            dic["cashtotal"] += ordermenu.totalprice
        else:
            dic["cashtotal"] = ordermenu.totalprice
    elif ordermenu.pay == 2:
        if "cardtotal" in dic:
            dic["cardtotal"] += ordermenu.totalprice
        else:
            dic["cardtotal"] = ordermenu.totalprice
    elif ordermenu.pay == 3:
        if "servicetotal" in dic:
            dic["servicetotal"] += ordermenu.totalprice
        else:
            dic["servicetotal"] = ordermenu.totalprice


def last_day_of_month(date, end):
    if date.year == end.year and date.month == end.month:
        return end
    elif date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month + 1, day=1) - timedelta(days=1)


def last_day_of_quarter(date, end):
    if date.month.real >= 1 and date.month.real <= 3:
        if end.year == date.year and end.month.real <= 3:
            return end
        else:
            return date.replace(month=4, day=1) - timedelta(days=1)
    elif date.month.real >= 4 and date.month.real <= 6:
        if end.year.real == date.year.real and end.month.real >= 4 and end.month.real <= 6:
            return end
        else:
            return date.replace(month=7, day=1) - timedelta(days=1)
    elif date.month.real >= 7 and date.month.real <= 9:
        if end.year.real == date.year.real and end.month.real >= 7 and end.month.real <= 9:
            return end
        else:
            return date.replace(month=10, day=1) - timedelta(days=1)
    elif date.month.real >= 10 and date.month.real <= 12:
        if end.year.real == date.year.real and end.month.real >= 10 and end.month.real <= 12:
            return end
        else:
            return date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)


def last_day_of_year(date, end):
    if end.year.real == date.year.real:
        return end
    else:
        return date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)


def line_chart(startDate, endDate, menus, unit):
    unit = int(unit)
    if unit < 1 or unit > 6:
        return {"error": "unit value is invalid"}
    start = datetime.strptime(startDate + " 00:00:00", '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(endDate + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
    current = start
    menu_name = {}
    count_for_result = -1

    def set_result(menus):
        result = {}
        for m in menus:
            menu = db.query(Menu).filter(Menu.id==m).first()
            menu_name[m] = menu.name
            result[menu.name] = []
        return result

    def init_hour_result(result):
        for m in result:
            for i in range(0, 24):
                result[m].append({})
                result[m][i]['price'] = 0
                result[m][i]['count'] = 0
                result[m][i]['cashtotal'] = 0
                result[m][i]['cardtotal'] = 0
                result[m][i]['servicetotal'] = 0
        return result

    def init_week_result(result):
        for m in result:
            for i in range(7):
                result[m].append({})
                result[m][i]['price'] = 0
                result[m][i]['count'] = 0
                result[m][i]['cashtotal'] = 0
                result[m][i]['cardtotal'] = 0
                result[m][i]['servicetotal'] = 0
        return result

    def init_result_per_unit(result):
        for m in result:
            result[m].append({'price': 0, 'count': 0, 'cashtotal': 0, 'cardtotal': 0, 'servicetotal': 0})
        return result


    result = set_result(menus)
    if unit == 1 or unit == 3:
        orders = db.query(Order).filter(start <= Order.time,
                                        Order.time <= end.replace(hour=23, minute=59, second=59)).all()
        if unit == 1:
            result = init_hour_result(result)
            for order in orders:
                for ordermenu in order.ordermenus:
                    if ordermenu.menu_id in menus:
                        result[menu_name[ordermenu.menu_id]][order.time.hour]['price'] += ordermenu.totalprice
                        result[menu_name[ordermenu.menu_id]][order.time.hour]['count'] += 1
                        increaseTotalPrice(ordermenu, result[menu_name[ordermenu.menu_id]][order.time.hour])
        elif unit == 3:
            result = init_week_result(result)
            for order in orders:
                for ordermenu in order.ordermenus:
                    if ordermenu.menu_id in menus:
                        result[menu_name[ordermenu.menu_id]][order.time.weekday()]['price'] += ordermenu.totalprice
                        result[menu_name[ordermenu.menu_id]][order.time.weekday()]['count'] += 1
                        increaseTotalPrice(ordermenu, result[menu_name[ordermenu.menu_id]][order.time.weekday()])
    else:
        while current <= end:
            if unit == 2:
                ordermenus = db.query(OrderMenu).join(Order).filter(current <= Order.time,
                                                                    Order.time <= current.replace(hour=23,
                                                                                                      minute=59,
                                                                                                      second=59)).all()
            elif unit == 4:
                month_last = last_day_of_month(current, end)
                ordermenus = db.query(OrderMenu).join(Order).filter(current <= Order.time,
                                                                    Order.time <= month_last).all()
                current = month_last
            elif unit == 5:
                quarter_month = last_day_of_quarter(current, end)
                ordermenus = db.query(OrderMenu).join(Order).filter(current <= Order.time,
                                                                    Order.time <= quarter_month).all()
                current = quarter_month
            elif unit == 6:
                last_year = last_day_of_year(current, end)
                ordermenus = db.query(OrderMenu).join(Order).filter(current <= Order.time,
                                                                     Order.time <= last_year).all()
                current = last_year
            result = init_result_per_unit(result)
            count_for_result += 1
            for ordermenu in ordermenus:
                if ordermenu.menu_id in menus:
                    result[menu_name[ordermenu.menu_id]][count_for_result]['price'] += ordermenu.totalprice
                    result[menu_name[ordermenu.menu_id]][count_for_result]['count'] += 1
                    increaseTotalPrice(ordermenu, result[menu_name[ordermenu.menu_id]][count_for_result])
            current = current + timedelta(days=1)
    return result


def bar_chart(startDate, endDate, menus, unit):
    unit = int(unit)
    if unit < 1 or unit > 6:
        return {'error': 'unit value is invalid'}
    start = datetime.strptime(startDate + " 00:00:00", '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(endDate + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
    current = start
    count_for_result = -1
    result = []
    def init_hour_result(result):
        for i in range(1, 25):
            result.append({'cashtotal': 0, 'cardtotal': 0,'totalprice': 0 , 'servicetotal': 0, 'count': 0})
        return result
    def init_week_result(result):
        for i in range(7):
            result.append({'cashtotal': 0, 'cardtotal': 0,'totalprice': 0 , 'servicetotal': 0, 'count': 0})
        return result
    def init_result_per_unit(result):
        result.append({'cashtotal': 0, 'cardtotal': 0, 'totalprice': 0 ,'servicetotal': 0, 'count': 0})
        return result

    if unit == 1 or unit == 3:
        orders = db.query(Order).filter(start <= Order.time,
                                        Order.time <= end.replace(hour=23, minute=59, second=59)).all()
        if unit == 1:
            result = init_hour_result(result)
            for order in orders:
                for ordermenu in order.ordermenus:
                    if ordermenu.menu_id in menus:
                        result[order.time.hour]['count'] += 1
                        result[order.time.hour]['totalprice'] += ordermenu.totalprice
                        increaseTotalPrice(ordermenu, result[order.time.hour])
        elif unit == 3:
            result = init_week_result(result)
            for order in orders:
                for ordermenu in order.ordermenus:
                    if ordermenu.menu_id in menus:
                        result[order.time.weekday()]['count'] += 1
                        result[order.time.weekday()]['totalprice'] += ordermenu.totalprice
                        increaseTotalPrice(ordermenu, result[order.time.weekday()])
    else:
        while current <= end:
            if unit == 2:
                ordermenus = db.query(OrderMenu).join(Order).filter(current <= Order.time,Order.time <= current.replace(hour=23,minute=59,second=59)).all()
            elif unit == 4:
                month_last = last_day_of_month(current, end)
                ordermenus = db.query(OrderMenu).join(Order).filter(current <= Order.time,Order.time <= month_last).all()
                current = month_last
            elif unit == 5:
                quarter_month = last_day_of_quarter(current, end)
                ordermenus = db.query(OrderMenu).join(Order).filter(current <= Order.time,
                                                                    Order.time <= quarter_month).all()
                current = quarter_month
            elif unit == 6:
                last_year = last_day_of_year(current, end)
                ordermenus = db.query(OrderMenu).join(Order).filter(current <= Order.time,Order.time <= last_year).all()
                current = last_year
            result = init_result_per_unit(result)
            count_for_result += 1
            for ordermenu in ordermenus:
                if ordermenu.menu_id in menus:
                    result[count_for_result]['count'] += 1
                    result[count_for_result]['totalprice'] += ordermenu.totalprice
                    increaseTotalPrice(ordermenu, result[count_for_result])
            current = current + timedelta(days=1)
    return result
    # 단위별 결제 방식, 총 결제방식 별 총액