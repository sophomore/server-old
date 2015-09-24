from datetime import datetime
from dateutil.relativedelta import relativedelta
from models import OrderMenu, Order, Menu
from mydb import db_session as db
import json

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
    menus = json.loads(menus)
    unit = int(unit)
    if unit<1 or unit>6:
        return {"error": "unit value is invalid"}

    startDateStart = datetime.strptime(startDate + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
    endDate = datetime.strptime(endDate + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
    currentDate = startDateStart
    temp = {}

    def increaseTotalPrice(ordermenu,dic):
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

    def getItem(result,item):
        for i in result:
            # print(i)
            if item in i:
                # print(item)
                return i
        return None

    def createResultDic(result,unit,currentDate):
        if not currentDate.year.real in temp:
            result[currentDate.year.real] = []
        if unit == 1:
            result = {}
            for i in range(0,24):
                result[i] = {}
                result[i]['menu'] = resetHourMenu()
        elif unit == 2:
            dic = getItem(result[currentDate.year.real],currentDate.month.real)
            if dic == None:
                result[currentDate.year.real].append({currentDate.month.real : {}})
            dic = getItem(result[currentDate.year.real],currentDate.month.real)
            print(dic)
            if dic != None:
                if not currentDate.day.real in dic[currentDate.month.real]:
                    dic[currentDate.month.real][currentDate.day.real] = {}
                    dic[currentDate.month.real][currentDate.day.real]['cashtotal'] = 0
                    dic[currentDate.month.real][currentDate.day.real]['cardtotal'] = 0
                    dic[currentDate.month.real][currentDate.day.real]['servicetotal'] = 0

        elif unit == 3:
            result = {}
            for i in ["일","월","화","수","목","금","토"]:
                result[i]={}
        elif unit == 4:
            dic = getItem(result[currentDate.year.real],currentDate.month.real)
            if dic  == None:
                result[currentDate.year.real].append({currentDate.month.real : {}})
                dic = getItem(result[currentDate.year.real],currentDate.month.real)
                dic[currentDate.month.real]['cashtotal'] = 0
                dic[currentDate.month.real]['cardtotal'] = 0
                dic[currentDate.month.real]['servicetotal'] = 0
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

    def resetMenus():
        menu = {}
        count = {}
        for m in menus:
            menu[m] = 0
            count[m] = 0
        return menu,count
    def resetHourMenu():
        menu = {}
        for m in menus:
            menu[m] = 0
        return menu

    total = 0
    def resetTotalAndCount(unit,currentDate,total,count,menus):

        if unit == 2:
            if increaseDate(2).day != currentDate.day:
                total = 0
                menus, count = resetMenus()
        elif unit == 4:
            if increaseDate(2).month != currentDate.month:
                total =0
                menus ,count = resetMenus()
                return total,count,menus
        return total,count,menus

    temp = createResultDic(temp,unit,currentDate)
    menu,count = resetMenus()
    if unit == 1:
            orders = db.query(Order).filter(startDate <= Order.time, Order.time <= endDate.replace(hour =23,minute = 59,second = 59)).all()
            for order in orders:
                for ordermenu in order.ordermenus:
                    if ordermenu.menu_id in temp[order.time.hour.real]:
                        temp[order.time.hour.real]['menu'][ordermenu.menu_id]['price'] += ordermenu.totalprice
                        temp[order.time.hour.real]['menu'][ordermenu.menu_id]['count'] +=1
                    increaseTotalPrice(ordermenu,temp[order.time.hour.real])
                    total += ordermenu.totalprice
                print(order)
    else:
        while currentDate<=endDate:
            temp = createResultDic(temp,unit,currentDate)
            ordermenus = db.query(OrderMenu).join(Order).filter(currentDate<= Order.time, Order.time <= currentDate.replace(hour=23,minute=59,second=59)).all()
            for ordermenu in ordermenus:
                total += ordermenu.totalprice
                if ordermenu.menu_id in menus:
                    menu[ordermenu.menu_id] += ordermenu.totalprice
                    count[ordermenu.menu_id] += 1


                if unit == 2:
                    dic = getItem(temp[currentDate.year.real],currentDate.month.real)
                    if dic != None:
                        increaseTotalPrice(ordermenu,dic[currentDate.month.real][currentDate.day.real])
                elif unit == 3:
                    pass
                elif unit == 4:
                    dic = getItem(temp[currentDate.year.real],currentDate.month.real)
                    if dic != None:
                        increaseTotalPrice(ordermenu,dic[currentDate.month.real])
                elif unit == 5:
                    if(currentDate.month.real>=1 and currentDate.month.real<=3):
                        increaseTotalPrice(ordermenu,temp[currentDate.year.real][1])
                    elif(currentDate.month.real>=4 and currentDate.month.real<=6):
                        increaseTotalPrice(ordermenu,temp[currentDate.year.real][2])
                    elif(currentDate.month.real>=7 and currentDate.month.real<=9):
                        increaseTotalPrice(ordermenu,temp[currentDate.year.real][3])
                    elif(currentDate.month.real>=10 and currentDate.month.real<=12):
                        increaseTotalPrice(ordermenu,temp[currentDate.year.real][4])
                elif unit == 6:
                    increaseTotalPrice(ordermenu,temp[currentDate.year])
            if unit == 2:
                dic = getItem(temp[currentDate.year.real],currentDate.month.real)
                if dic!=None:
                    setTotalAndMenus(dic[currentDate.month.real][currentDate.day.real],count,total,menu)
            elif unit == 4:
                dic = getItem(temp[currentDate.year.real],currentDate.month.real)
                if dic != None:
                    setTotalAndMenus(dic,count,total,menu)
            total, count,menu = resetTotalAndCount(unit,currentDate,total,count,menu)
            currentDate = increaseDate(2)

    result = temp
    return result

#단위별 결제 방식, 총 결제방식 별 총액