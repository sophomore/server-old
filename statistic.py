from datetime import datetime
from dateutil.relativedelta import relativedelta
from models import OrderMenu, Order, Menu
from mydb import db_session as db
import json


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
        if item in result:
            return result[item]
        return None
    def createResultDic(result,unit,currentDate):
        if not currentDate.year.real in result:
            result[currentDate.year.real] = {}
        if unit == 1:
            result = {}
            for i in range(0,24):
                result[i] = {}
                result[i]['cashtotal'] = 0
                result[i]['cardtotal'] = 0
                result[i]['servicetotal'] = 0
                result[i]['menu'] = resetHourMenu()
        elif unit == 2:
            dic = getItem(result[currentDate.year.real],currentDate.month.real)
            if dic == None:
                result[currentDate.year.real][currentDate.month.real]={}
            dic = getItem(result[currentDate.year.real],currentDate.month.real)
            if dic != None:
                if not currentDate.day.real in dic:
                    dic[currentDate.day.real] = {}

                    dic[currentDate.day.real]['cashtotal'] = 0
                    dic[currentDate.day.real]['cardtotal'] = 0
                    dic[currentDate.day.real]['servicetotal'] = 0
        elif unit == 3:
            result = {}
            for i in [0,1,2,3,4,5,6]:
                result[i]={}
                result[i]['cashtotal'] = 0
                result[i]['cardtotal'] = 0
                result[i]['servicetotal'] = 0
                result[i]['menu'] ,result[i]['count'] = resetMenus()
        elif unit == 4:
            dic = getItem(result[currentDate.year.real],currentDate.month.real)
            if dic  == None:
                result[currentDate.year.real][currentDate.month.real] = {}
                dic = getItem(result[currentDate.year.real],currentDate.month.real)
                dic['cashtotal'] = 0
                dic['cardtotal'] = 0
                dic['servicetotal'] = 0
        elif unit == 5:
            if currentDate.month.real>=1 and currentDate.month.real<=3:
                dic = getItem(result[currentDate.year.real],1)
                if dic == None:
                    result[currentDate.year.real][1]={}
                    dic2 = getItem(result[currentDate.year.real],1)
                    dic2['cashtotal'] = 0
                    dic2['cardtotal'] = 0
                    dic2['servicetotal'] = 0
                    dic2['menu'], dic2['count'] = resetMenus()
            elif currentDate.month.real>=4 and currentDate.month.real<=6:
                dic = getItem(result[currentDate.year.real],2)
                if dic == None:
                    result[currentDate.year.real][2] = {}
                    dic2 = getItem(result[currentDate.year.real],2)
                    dic2['cashtotal'] = 0
                    dic2['cardtotal'] = 0
                    dic2['servicetotal'] = 0
                    dic2['menu'], dic2['count'] = resetMenus()
            elif currentDate.month.real>=7 and currentDate.month.real<=9:
                dic = getItem(result[currentDate.year.real],3)
                if dic == None:
                    result[currentDate.year.real][3] = {}
                    dic2 = getItem(result[currentDate.year.real],3)
                    dic2['cashtotal'] = 0
                    dic2['cardtotal'] = 0
                    dic2['servicetotal'] = 0
                    dic2['menu'], dic2['count'] = resetMenus()
            elif currentDate.month.real>=10 and currentDate.month.real<=12:
                dic = getItem(result[currentDate.year.real],4)
                if dic == None:
                    result[currentDate.year.real][4] = {}
                    dic2 = getItem(result[currentDate.year.real],4)
                    dic2['cashtotal'] = 0
                    dic2['cardtotal'] = 0
                    dic2['servicetotal'] = 0
                    dic2['menu'], dic2['count'] = resetMenus()
        elif unit == 6:
            result[currentDate.year.real]['cashtotal'] = 0
            result[currentDate.year.real]['cardtotal'] = 0
            result[currentDate.year.real]['servicetotal'] = 0
            result[currentDate.year.real]['menu'],result[currentDate.year.real]['count'] = resetMenus()
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

    def last_day_of_month(date):
        if date.month == 12:
            return date.replace(day=31)
        return date.replace(month=date.month+1, day=1) - relativedelta(days=1)

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
            menu[int(m)] = {}
            menu[int(m)]['price'] = 0
            menu[int(m)]['count'] = 0
        return menu

    total = 0
    def resetTotalAndCount(unit,currentDate,total,count,menus):
        if unit == 2:
            total = 0
            menus, count = resetMenus()
        elif unit == 4:
            total =0
            menus ,count = resetMenus()
            return total,count,menus
        elif unit == 5:
            if currentDate.month.real>=1 and currentDate.month.real<=3:
                if increaseDate(2).month.real>3:
                    total = 0
                    menus,count = resetMenus()
                    return total,count,menus
            elif currentDate.month.real>=4 and currentDate.month.real<=6:
                if increaseDate(2).month.real>6:
                    total = 0
                    menus,count = resetMenus()
                    return total,count,menus
            elif currentDate.month.real>=7 and currentDate.month.real<=9:
                if increaseDate(2).month.real>9:
                    total = 0
                    menus,count = resetMenus()
                    return total,count,menus
            elif currentDate.month.real>=10 and currentDate.month.real<=12:
                if increaseDate(2).month.real<10:
                    total = 0
                    menus,count = resetMenus()
                    return total,count,menus
        elif unit == 6:
            if increaseDate(2).year.real != currentDate.year.real:
                total = 0
                menus, count = resetMenus()
        return total,count,menus

    menu,count = resetMenus()
    if unit == 1 or unit == 3:
        temp = createResultDic(temp,unit,currentDate)
        orders = db.query(Order).filter(startDate <= Order.time, Order.time <= endDate.replace(hour =23,minute = 59,second = 59)).all()
        if unit == 1:
            for order in orders:
                for ordermenu in order.ordermenus:
                    if ordermenu.menu_id in temp[order.time.hour.real]['menu']:
                        temp[order.time.hour.real]['menu'][ordermenu.menu_id]['price'] += ordermenu.totalprice
                        temp[order.time.hour.real]['menu'][ordermenu.menu_id]['count'] +=1
                    increaseTotalPrice(ordermenu,temp[order.time.hour.real])
                    total += ordermenu.totalprice
        elif unit == 3:
           for order in orders:
               for ordermenu in order.ordermenus:
                   if ordermenu.menu_id in temp[order.time.weekday()]['menu']:
                       temp[order.time.weekday()]['menu'][ordermenu.menu_id] += ordermenu.totalprice
                       temp[order.time.weekday()]['count'][ordermenu.menu_id] += 1
                   increaseTotalPrice(ordermenu,temp[order.time.weekday()])
                   total += ordermenu.totalprice
    else:
        while currentDate<=endDate:
            print(currentDate)
            if unit == 2:
                temp = createResultDic(temp,unit,currentDate)
                ordermenus = db.query(OrderMenu).join(Order).filter(currentDate<= Order.time, Order.time <= currentDate.replace(hour=23,minute=59,second=59)).all()
            else:
                if currentDate.year == endDate.year and currentDate.month == endDate.month:
                    ordermenus = db.query(OrderMenu).join(Order).filter(currentDate<= Order.time, Order.time <= endDate).all()
                    currentDate = endDate
                    temp = createResultDic(temp,unit,currentDate)
                else:
                    month_last = last_day_of_month(currentDate)
                    ordermenus = db.query(OrderMenu).join(Order).filter(currentDate<= Order.time, Order.time <= month_last).all()
                    currentDate = month_last
                    temp = createResultDic(temp,unit,currentDate)
            for ordermenu in ordermenus:
                total += ordermenu.totalprice
                if ordermenu.menu_id in menus:
                    menu[ordermenu.menu_id] += ordermenu.totalprice
                    count[ordermenu.menu_id] += 1
                if unit == 2:
                    dic = getItem(temp[currentDate.year.real],currentDate.month.real)
                    if dic != None:
                        increaseTotalPrice(ordermenu,dic[currentDate.day.real])
                elif unit == 4:
                    dic = getItem(temp[currentDate.year.real],currentDate.month.real)
                    if dic != None:
                        increaseTotalPrice(ordermenu,dic)
                elif unit == 5:
                    if(currentDate.month.real>=1 and currentDate.month.real<=3):
                        dic = getItem(temp[currentDate.year.real],1)
                        if dic != None:
                            increaseTotalPrice(ordermenu,dic)
                    elif(currentDate.month.real>=4 and currentDate.month.real<=6):
                        dic = getItem(temp[currentDate.year.real],2)
                        if dic != None:
                            increaseTotalPrice(ordermenu,dic)
                    elif(currentDate.month.real>=7 and currentDate.month.real<=9):
                        dic = getItem(temp[currentDate.year.real],3)
                        if dic != None:
                            increaseTotalPrice(ordermenu,dic)
                    elif(currentDate.month.real>=10 and currentDate.month.real<=12):
                        dic = getItem(temp[currentDate.year.real],4)
                        if dic != None:
                            increaseTotalPrice(ordermenu,dic)
                elif unit == 6:
                    increaseTotalPrice(ordermenu,temp[currentDate.year])
            if unit == 2:
                dic = getItem(temp[currentDate.year.real],currentDate.month.real)
                if dic!=None:
                    setTotalAndMenus(dic[currentDate.day.real],count,total,menu)
            elif unit == 4:
                dic = getItem(temp[currentDate.year.real],currentDate.month.real)
                if dic != None:
                    setTotalAndMenus(dic,count,total,menu)
            elif unit == 5:
                if currentDate.month.real>=1 and currentDate.month.real<=3:
                    dic = getItem(temp[currentDate.year.real],1)
                    if dic!=None:
                        setTotalAndMenus(dic[1],count,total,menu)
                elif currentDate.month.real>=4 and currentDate.month.real<=6:
                    dic = getItem(temp[currentDate.year.real],2)
                    if dic!=None:
                        setTotalAndMenus(dic[2],count,total,menu)
                elif currentDate.month.real>=7 and currentDate.month.real<=9:
                    dic = getItem(temp[currentDate.year.real],3)
                    if dic!=None:
                        setTotalAndMenus(dic[3],count,total,menu)
                elif currentDate.month.real>=10 and currentDate.month.real<=12:
                    dic = getItem(temp[currentDate.year.real],4)
                    if dic!=None:
                        setTotalAndMenus(dic[4],count,total,menu)
            elif unit == 6:
                setTotalAndMenus(temp[currentDate.year.real],count,total,menu)
            total, count,menu = resetTotalAndCount(unit,currentDate,total,count,menu)
            currentDate = increaseDate(2)
    return temp

#단위별 결제 방식, 총 결제방식 별 총액