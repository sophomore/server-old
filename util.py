import csv
import os
from openpyxl import load_workbook
from datetime import datetime
from models import OrderMenu, Order, Menu
from mydb import db_session as db
import time

def print_receipt(ordermenus):
	menus = db.query(Menu).all()
	ms = [""]
	order = {}
	curry = {}
	twice = {}
	takeout = {}
	t_curry = {}
	t_twice = {}
	for menu in menus:
		ms.append(menu.name)
	for ordermenu in ordermenus:
		name = ms[ordermenu.menu_id]
		if not ordermenu.takeout:
			if name in order:
				order[name] += 1
			else:
				order[name] = 1
				curry[name] = 0
				twice[name] = 0
			if ordermenu.curry:
				curry[name] +=1
			if ordermenu.twice:
				twice[name] +=1
		else:
			if name in takeout:
				takeout[name] += 1
			else:
				takeout[name] = 1
				t_curry[name] = 0
				t_twice[name] = 0
			if ordermenu.curry:
				t_curry[name] +=1
			if ordermenu.twice:
				t_twice[name] +=1
	string = u'\x1b\x44\x04\x0e\x00'
	string +=u'메    뉴    수량'
	for key in order:
		string += u''+key+'\n'
		string += u'\x09일반\x09'+str(order[key]-curry[key]-twice[key])+'\n'
		if order[key+curry]>0:
			string += u'\x09카레\x09'+str(curry[key])+'\n'
		if order[key+twice]>0:
			string += u'\x09  곱\x09'+str(twice[key])+'\n'
	string += u'---------------------------------\n'
	for key in takeout:
		string += u''+key+'\n'
		string += u'\x09일반\x09'+str(takeout[key]-t_curry[key]-t_twice[key])+'\n'
		if takeout[key+curry]>0:
			string += u'\x09카레\x09'+str(t_curry[key])+'\n'
		if takeout[key+twice]>0:
			string += u'\x09  곱\x09'+str(t_curry[key])+'\n\n\n\n\n'
	string += u'\x1bm'
	f1 = open('./test','w+',encoding="euc-kr")
	print(output,file = f1)
	f1.close()
	os.system('lpr -P RECEIPT_PRINTER test')
def print_statement(orders):
    menus = db.query(Menu).all()
    ms = [""]
    price = {}
    order = {}
    curry = 0
    twice = 0
    for menu in menus:
        ms.append(menu.name)
        price[menu.name] = menu.price
    for ordermenu in orders.ordermenus:
        name = ms[ordermenu[ordermenu.menu_id]]
        if name in order:
            order[name] += order[name]+1
        else:
            order[name] = 1
        if ordermenu['curry']:
            curry+=1
        if ordermenu['twice']:
            twice +=1
    orderstring = ''
    for o in order:
        orderstring +=u''+o+'\x09'+str(order[o])+'\x09'+str(price[o])+'\x09'+str(order[o]*price[o])+'\n'
    if curry>0:
        orderstring +=u'카레추가\x09'+str(curry)+'\x092500\x09'+str(2500*curry)+'\n'
    if twice>0:
        orderstring +=u'곱배기\x09'+str(twice)+'\x092500\x09'+str(2500*twice)+'\n'

    output =u'\x1b\x44\x0d\x12\x19\x00\x1b\x24\x00\x02'
    output +=u'상 호 명: 송호성 쉐프의 돈까스\n'
    output +=u'등록번호: 134-31-16828\n'
    output +=u'대   표: 송호성\n'
    output +=u'전화번호: 031-480-4595\n'
    output +=u'주   소: 경기 안산시 상록구 사동 1165번지\n\n'
    output +=u'주문:'+ordertime+'\n'
    output +=u'---------------------------------\n'
    output +=u'상 품 명'.center(6)+'  수량'.center(2)+'  단가'.center(5)+'   금 액'.center(6)+'\n'
    output +=u''+orderstring
    output +=u'---------------------------------\n\n\n\n\n\n\n\n'
    output +=u'\x1bm'
    f1 = open('./test','w+',encoding="euc-kr")
    print(output,file = f1)
    f1.close()
    os.system('lpr -P RECEIPT_PRINTER test')



def output():
    os.system("mysqldump --user=song --password=Qoswlfdlsnrn pos > ./backup.sql")

def input_two():
    os.system("mysql --user=song --password=Qoswlfdlsnrn pos < backup.sql")

def input():
    menus = db.query(Menu).all()
    ms = {}
    price = {}
    for menu in menus:
        ms[menu.name] = menu.id;
        price[menu.name] = menu.price
    wb = load_workbook(filename='../backup.xlsx',read_only = True)
    ws = wb['입출금관리']
    a = lambda x: x>0
    takeout = lambda x: x=="배달"
    f = open("../menus.txt",'w')
    for row in ws.iter_rows(row_offset=1):
        if str(row[0].value) == "합 계":
            break
        else:
            date = str(row[0].value)+' '+str(row[2].value)+':00'
        totalprice = row[6]
        order = Order(date,totalprice)
        db.add(order)
        count_twice = get_sign(str(row[13].value),"곱배기추가")
        count_curry = get_sign(str(row[13].value),"카레추가")
        if int(row[8].value) == 0:
            pay = 2
        elif int(row[9].value) ==0:
            pay = 1
        else:
            pay = 4
        ordermenus = str(row[13].value).split(",")
        for o in ordermenus:
            if o.endswith(")"):
                bef,m,aft = o.partition("(")
                num,m,aft = aft.partition(")")
                for i in range(int(num)):
                    if bef in ms and (bef != "곱배기추가" and bef != "카레추가"):
                        ordermenu = OrderMenu(menu=ms[bef],order=order, pay=pay,curry=a(count_curry),
                        twice=a(count_twice),takeout=takeout(str(row[3].value)))
                        db.add(ordermenu)
                    elif bef!="곱배기추가" and bef!="카레추가":
                        f.write(bef)
                    count_twice = count_twice - 1
                    count_curry = count_curry - 1
            else:
                if o in ms and (o != "곱배기추가" and o != "카레추가"):
                    ordermenu = OrderMenu(menu=ms[o],order=order,pay=pay,curry=a(count_curry),
                    twice=(count_twice),takeout=takeout(str(row[3].value)))
                    db.add(ordermenu)
                elif o != "곱배기추가" and o != "카레추가":
                    f.write(o)
                count_twice = count_twice - 1
                count_curry = count_curry - 1 
        db.commit()
        f.write('\n')
    f.close()

def get_sign(strg,st):
    bef,m,aft = strg.partition(st)
    if aft != "" and aft.startswith("("):
        bef,m,aft = aft[1:].partition(")")
        count = bef
    elif aft.startswith(","):
        count = 1
    else:
        count = 0
    return count

