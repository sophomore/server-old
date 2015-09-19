from datetime import datetime
from dateutil.relativedelta import relativedelta
from models import OrderMenu, Order, Menu
from mydb import db_session as db

#in : 기간, out : 월별로 메뉴별 금액 총합, 월별 전체 총합 및 개수, etc : 카레추가, 곱배기 금액 포함
def month_money_sum(startDateStr, endDateStr):
    result = {}
    result['debug2'] = ""

    startDate = datetime.strptime(startDateStr+' 00:00:00', '%Y-%m-%d %H:%M:%S')
    while True:
        endDate = startDate + relativedelta(months=1)

        if endDate >= datetime.strptime(endDateStr+' 00:00:00', '%Y-%m-%d %H:%M:%S'):
            break;

        ordermenus = db.query(OrderMenu).join(Order, Order.id == OrderMenu.order_id).filter(Order.time >= startDate).filter(Order.time <= endDate)
        print(ordermenus)
        result['debug2'] += " | "+str(ordermenus)

        # menus = {}
        # total = 0
        # count = 0
        # for ordermenu in ordermenus:
        #     if ordermenu.menu_id in menus:
        #         menus[ordermenu.menu_id] += ordermenu.totalprice
        #     else:
        #         menus[ordermenu.menu_id] = ordermenu.totalprice
        #     count += 1
        #     total += ordermenu.totalprice
        #
        # result[startDate.year.real] = {startDate.month.real: {"menu": menus, "total": total, "count": count}}
        startDate = endDate
    return result


#in 기간, 메뉴리스트, 단위 out 단위에 맞춰서 각 메뉴별 총액 및 개수
#unit : 1. 시간, 2. 일, 3. 요일, 4. 월, 5. 분기, 6. 년
def unit_menu_sum(startDate, endDate, menus, unit):
    if int(unit)<1 or int(unit)>6:
        return {"error": "unit value is invalid"}

    startDateStart = datetime.strptime(startDate + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
    endDate = datetime.strptime(endDate + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
    currentDate = startDateStart
    def last_day_of_month(date):
        if date.month == 12:
            return date.replace(day=31)
        return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)

    def first_day_of_month(date):
        return date.replace(month=date.month, day=1)

    def first_day_of_next_month(date):
        if date.month ==12:
            return date.replace(year=date.year+1,month=1,day=1)
        return date.replace(month=date.month+1,day =1)

    def increaseDate(unit):
        if unit == 1:
            return currentDate + relativedelta(hours=1)
        elif unit == 2:
            return currentDate + relativedelta(days=1)
        elif unit == 3:
            return currentDate + relativedelta(weeks=1)
        elif unit == 4:
            return currentDate + relativedelta(months=1)
        elif unit == 5:
            return currentDate + relativedelta(months=3)
        elif unit == 6:
            return currentDate + relativedelta(years=1)
    result = {}
    result[currentDate.year.real]={}
    result[currentDate.year.real][currentDate.month.real]={}
    result[currentDate.year.real][currentDate.month.real]["total"] = 0
    result[currentDate.year.real][currentDate.month.real]["cashtotal"] = 0
    result[currentDate.year.real][currentDate.month.real]["cardtotal"] = 0
    result[currentDate.year.real][currentDate.month.real]["servicetotal"] = 0
    result[currentDate.year.real][currentDate.month.real]["credittotal"] = 0
    result[currentDate.year.real][currentDate.month.real]["count"] = 0
    result['debug'] = 0
    count2 = 0
    while currentDate<=endDate:
        ordermenus = db.query(OrderMenu).filter(currentDate <= Order.time, Order.time <= currentDate.replace(hour=23,minute=59,second=59)).all()
        count2 +=1
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
            if unit == 4:
                result['debug'] += ordermenu.pay
                if ordermenu.pay == 1:
                    result[currentDate.year.real.real][currentDate.month.real.real]["cashtotal"] += ordermenu.totalprice
                    result['debug'] += str(ordermenu.totalprice)+"$"
                elif ordermenu.pay == 2:
                    result[currentDate.year.real][currentDate.month.real]["cardtotal"] += ordermenu.totalprice
                elif ordermenu.pay == 3:
                    result[currentDate.year.real][currentDate.month.real]["servicetotal"] += ordermenu.totalprice
                result[currentDate.year.real][currentDate.month.real]["total"] += ordermenu.totalprice

        if unit == 4:
            result[currentDate.year.real][currentDate.month.real]['menu'] = menus
            result[currentDate.year.real][currentDate.month.real]['total'] = total

        currentDate = increaseDate(2)
    return result

#단위별 결제 방식, 총 결제방식 별 총액