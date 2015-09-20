from datetime import datetime
from dateutil.relativedelta import relativedelta
from models import OrderMenu, Order, Menu
from mydb import db_session as db

#in : 기간, out : 월별로 메뉴별 금액 총합, 월별 전체 총합 및 개수, etc : 카레추가, 곱배기 금액 포함
def month_money_sum(startDateStr, endDateStr):
    result = []
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
    unit = int(unit)
    if unit<1 or unit>6:
        return {"error": "unit value is invalid"}

    startDateStart = datetime.strptime(startDate + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
    endDate = datetime.strptime(endDate + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
    currentDate = startDateStart
    result = {}
    temp = {}

    def increaseTotalPrice(ordermenu,dic):
        result['debug'] = 'come'
        if ordermenu.pay == 1:
            if "cashtotal" in dic:
                dic["cashtotal"] += ordermenu.totalprice
                result['debug2'] = dic['cashtotal']
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

    def createResultDic(result,unit,currentDate):
        if not currentDate.year.real in temp:
            temp[currentDate.year.real] = {}
            result[currentDate.year.real] = {}
        if unit == 1:
            for i in range(1,24):
                result[i] = {}
                result[i]['menu'] = {}
        elif unit == 2:
            if not currentDate.month.real in result[currentDate.year.real]:
                result[currentDate.year.real][currentDate.month.real] = {}
            result[currentDate.year.real][currentDate.month.real][currentDate.day.real] = {}
        elif unit == 3:
            result = {}
            for i in ["일","월","화","수","목","금","토"]:
                result[i]={}
        elif unit == 4:
            if not currentDate.month.real in temp[currentDate.year.real]:
                temp[currentDate.year.real][currentDate.month.real] = {}
                result[currentDate.year.real][currentDate.month.real]={}
        elif unit == 5:
            if not 1 in result[currentDate.year.real]:
                result[currentDate.year.real][1]={}
                result[currentDate.year.real][2]={}
                result[currentDate.year.real][3]={}
                result[currentDate.year.real][4]={}
        return result

    def setTotalAndMenus(dic,count,total,menus):
        dic['count'] = count
        dic['menu'] = menus
        dic['total'] = total

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



    result = createResultDic(result,unit,currentDate)
    result['debug'] = "start"
    result['debug2'] = 0
    while currentDate<=endDate:
        result = createResultDic(result,unit,currentDate)
        menus = {}
        total = 0
        count = 0
        if unit == 1:
            orders = db.query(Order).filter(currentDate <= Order.time, Order.time <= currentDate.replace(hour =23,minute = 59,second = 59)).all()
            for order in orders:
                for ordermenu in order.ordermenus:
                    if ordermenu.menu_id in result[order.time.hour.real]:
                        result[order.time.hour.real][ordermenu.menu_id] += ordermenu.totalprice
                    else:
                        result[order.time.hour.real][ordermenu.menu_id] = ordermenu.totalprice
                    increaseTotalPrice(ordermenu,result[order.time.hour.real])
                    count +=1
                    total += ordermenu.totalprice

            result['debug2']+= order.__sizeof__()
        else:
            ordermenus = db.query(OrderMenu).filter(currentDate <= Order.time, Order.time <= currentDate.replace(hour=23,minute=59,second=59)).all()
            for ordermenu in ordermenus:
                if ordermenu.menu_id in menus:
                    menus[ordermenu.menu_id] += ordermenu.totalprice
                else:
                    menus[ordermenu.menu_id] = ordermenu.totalprice

                count += 1
                total += ordermenu.totalprice

                if unit == 2:
                    increaseTotalPrice(ordermenu,result[currentDate.year.real][currentDate.month.real][currentDate.day.real])
                elif unit == 3:
                    pass
                elif unit == 4:
                    increaseTotalPrice(ordermenu,result[currentDate.year.real][currentDate.month.real])
                elif unit == 5:
                    if(currentDate.month.real>=1 and currentDate.month.real<=3):
                        increaseTotalPrice(ordermenu,result[currentDate.year.real][1])
                    elif(currentDate.month.real>=4 and currentDate.month.real<=6):
                        increaseTotalPrice(ordermenu,result[currentDate.year.real][2])
                    elif(currentDate.month.real>=7 and currentDate.month.real<=9):
                        increaseTotalPrice(ordermenu,result[currentDate.year.real][3])
                    elif(currentDate.month.real>=10 and currentDate.month.real<=12):
                        increaseTotalPrice(ordermenu,result[currentDate.year.real][4])
                elif unit == 6:
                    increaseTotalPrice(ordermenu,result[currentDate.year])
        if unit == 4:
            setTotalAndMenus(result[currentDate.year.real][currentDate.month.real],count,total,menus)

        currentDate = increaseDate(2)
    return result

#단위별 결제 방식, 총 결제방식 별 총액