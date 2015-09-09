from datetime import datetime
from models import OrderMenu, Order, Menu
from mydb import db_session as db

#in : 기간, out : 월별 메뉴 금액 총합
def month_money_sum(startYear, startMonth, endYear, endMonth):
    startDate = datetime.strptime(str(startYear)+'-'+str(startMonth), '%Y-%m')
    endDate = datetime.strptime(str(endYear)+'-'+str(endMonth), '%Y-%m')
    orders = Order.query.filter(Order.time >= startDate, Order.time < endDate).all()

    result = {}
    for order in orders:
        ordermenus = order.ordermenus
        result[str(startYear)+'-'+str(startMonth)] = []
        menuprice = {}
        for ordermenu in ordermenus:
            if ordermenu.menu_id in menuprice.keys():
                menuprice[ordermenu.menu_id] = (Menu.query.filter_by(id=ordermenu.menu_id).fitst()).totalprice
            else:
                menuprice[ordermenu.menu_id] += (Menu.query.filter_by(id=ordermenu.menu_id).fitst()).totalprice
        result[str(startYear)+'-'+str(startMonth)].append({"totalprice": order.totalprice})
        result[str(startYear)+'-'+str(startMonth)].append({"menutotal": menuprice})
        if startMonth >= 12:
            startYear += 1
            startMonth = 1

    return result


#in 기간,메뉴리스트, 단위 out 단위에 맞춰서 각 메뉴별 총액