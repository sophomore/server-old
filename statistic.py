from datetime import datetime
from dateutil.relativedelta import relativedelta
from models import OrderMenu, Order, Menu
from mydb import db_session as db

#in : 기간, out : 월별로 메뉴별 금액 총합, 월별 전체 총합 및 개수, etc : 카레추가, 곱배기 금액 포함
def month_money_sum(startDateStr, endDateStr):
    result = {}
    result['debug'] = startDateStr+" "+endDateStr

    startDate = datetime.strptime(startDateStr+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    while True:
        endDate = startDate + relativedelta(months=1)

        if endDate >= datetime.strptime(endDateStr+' 00:00:00', '%Y-%m-%d %H:%M:%S'):
            break;

        # ordermenus = db.query(OrderMenu).filter(Order.time >= startDate, Order.time <= endDate).all()
        orders = Order.query.filter(startDate <= Order.time, Order.time <= endDate).all()
        ordermenus = []
        for order in orders:
            ordermenus += order.ordermenus
        result['debug1'] += " | "+str(orders)
        result['debug2'] += " | "+str(ordermenus)

        menus = {}
        total = 0
        count = 0
        for ordermenu in ordermenus:
            if ordermenu.menu_id in menus:
                menus[ordermenu.menu_id] += ordermenu.totalprice
            else:
                menus[ordermenu.menu_id] = ordermenu.totalprice
            count += 1
            total += ordermenu.totalprice

        result[startDate.year.real] = {startDate.month.real: {"menu": menus, "total": total, "count": count}}
        startDate = endDate
    return result


#in 기간, 메뉴리스트, 단위 out 단위에 맞춰서 각 메뉴별 총액 및 개수
#unit : 1. 시간, 2. 일, 3. 요일, 4. 월, 5. 분기, 6. 년
def unit_menu_sum(startDate, endDate, menus, unit):

    def increaseDate(unit):
        if unit == 1:
            return startDate + relativedelta(hours=1)
        elif unit == 2:
            return startDate + relativedelta(days=1)
        elif unit == 3:
            return startDate + relativedelta(weeks=1)
        elif unit == 4:
            return startDate + relativedelta(months=1)
        elif unit == 5:
            return startDate + relativedelta(months=3)
        elif unit == 6:
            return startDate + relativedelta(years=1)

    result = {}
    while True:
        if unit == 3:
            pass
        elif unit == 5:
            pass
        currentDate = increaseDate(unit)

        if currentDate >= endDate:
            break;

        ordermenus = db.query(OrderMenu).filter(startDate <= Order.time, Order.time <= currentDate).all()

        menus = {}
        total = 0
        count = 0
        for ordermenu in ordermenus:
            if ordermenu.menu_id in menus:
                menus[ordermenu.menu_id] += ordermenu.totalprice
            else:
                menus[ordermenu.menu_id] = ordermenu.totalprice
            count += 1
            total += ordermenu.totalprice
        if unit == 6:
            result[startDate.year.real] = {"menu": menus, "total": total, "count":count}
        else:
            if not startDate.year.real in result:
                result[startDate.year.real] = {}
            if unit == 4:
                result[startDate.year.real][startDate.month.real] = {"menu": menus, "total": total, "count":count}
            else:
                # if not startDate.month.real in result[]
                pass
    if unit == 1:
        pass
    elif unit == 2:
        pass
    elif unit == 3:
        pass
    elif unit == 4:
        pass
    elif unit == 5:
        pass
    elif unit == 6:
        pass
    else:
        return {"error": "unit value is invalid"}

#단위별 결제 방식, 총 결제방식 별 총액