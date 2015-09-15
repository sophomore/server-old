from datetime import datetime
from dateutil.relativedelta import relativedelta
from models import OrderMenu, Order, Menu
from mydb import db_session as db

#in : 기간, out : 월별로 메뉴별 금액 총합, 월별 전체 총합, etc : 카레추가, 곱배기 금액 포함
def month_money_sum(startDateStr, endDateStr):
    result = {}

    startDate = datetime.strptime(startDateStr+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    while True:
        endDate = startDate + relativedelta(months=1)

        if endDate == datetime.strptime(endDateStr+' 00:00:00', '%Y-%m-%d %H:%M:%S'):
            break;

        ordermenus = db.query(OrderMenu).filter(Order.time >= startDate, Order.time < endDate).all()

        menus = {}
        total = 0
        for ordermenu in ordermenus:
            if ordermenu.menu_id in menus:
                menus[ordermenu.menu_id] += ordermenu.totalprice
            else:
                menus[ordermenu.menu_id] = ordermenu.totalprice
            total += ordermenu.totalprice

        result[startDate.year.real] = {startDate.month.real: {"menu": menus, "total": total}}
        startDate = endDate
    return result


#in 기간,메뉴리스트, 단위 out 단위에 맞춰서 각 메뉴별 총액
def unit_menu_sum(startDate, endDate, menus, unit):
    pass

#단위별 결제 방식, 총 결제방식 별 총액