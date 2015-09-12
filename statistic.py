from datetime import datetime
from dateutil.relativedelta import relativedelta
from models import OrderMenu, Order, Menu
from mydb import db_session as db

#in : 기간, out : 월별 메뉴 금액 총합
def month_money_sum(startYear, startMonth, endYear, endMonth):
    # startDate = datetime.strptime(str(startYear)+'-'+str(startMonth), '%Y-%m')
    # endDate = datetime.strptime(str(endYear)+'-'+str(endMonth), '%Y-%m')
    # orders = Order.query.filter(Order.time >= startDate, Order.time < endDate).all()

    # available_menus = Menu.query.filter_by(Menu.available==True).all()
    result = {}

    startDate = datetime.strptime(str(startYear)+'-'+str(startMonth)+'-01 00:00:00', '%Y-%m-%d %H:%M:%S')
    while True:
        endDate = startDate + relativedelta(months=1)

        print(startDate, endDate, datetime.strptime(str(endYear)+'-'+str(endMonth)+'-01 00:00:00', '%Y-%m-%d %H:%M:%S'))

        if endDate == datetime.strptime(str(endYear)+'-'+str(endMonth)+'-01 00:00:00', '%Y-%m-%d %H:%M:%S'):
            break;

        result[startDate.month.real] = db.query(OrderMenu, Order).filter(Order.time >= startDate, Order.time < endDate).all()
        startDate = endDate

    # result = {}
    # for order in orders:
    #     ordermenus = order.ordermenus
    #     result[str(startYear)+'-'+str(startMonth)] = []
    #     menuprice = {}
    #     for ordermenu in ordermenus:
    #         if ordermenu.menu_id in menuprice.keys():
    #             menuprice[ordermenu.menu_id] = (Menu.query.filter_by(id=ordermenu.menu_id).fitst()).totalprice
    #         else:
    #             menuprice[ordermenu.menu_id] += (Menu.query.filter_by(id=ordermenu.menu_id).fitst()).totalprice
    #     result[str(startYear)+'-'+str(startMonth)].append({"totalprice": order.totalprice})
    #     result[str(startYear)+'-'+str(startMonth)].append({"menutotal": menuprice})
    #     if startMonth >= 12:
    #         startYear += 1
    #         startMonth = 1

    return result


#in 기간,메뉴리스트, 단위 out 단위에 맞춰서 각 메뉴별 총액

#단위별 결제 방식, 총 결제방식 별 총액