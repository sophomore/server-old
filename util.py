import csv
import os
from openpyxl import load_workbook
from datetime import datetime
from models import OrderMenu, Order, Menu
from mydb import db_session as db


def print_statement(order,time):

    output = ''
    output +=u'상 호 명: 송호성 쉐프의 돈까스\n'
    output +=u'등록번호: 134-31-16828\n'
    output +=u'대   표: 송호성\n'
    output +=u'전화번호: 031-480-4595\n'
    output +=u'주   소: 경기 안산시 상록구 사동 1165번지\n\n'
    output +=u'주문:'+time
    output +=u'---------------------------------\n'
    output +=u'상 품 명'.center(6)+'수량'.center(2)+'단가'.center(5)+'금 액'.center(6)
    output +=u''+order
    output +=u'---------------------------------\n'
    output +=u'\x1bm'
    f1 = open('./test','w+')
    print(output,file = f1)
    f1.close()
    os.system('lpr test')



def output():
    os.system("mysqldump --user=song --password=Qoswlfdlsnrn pos > ./backup.sql")

def input_two():
    os.system("mysql --user=song --password=Qoswlfdlsnrn pos < backup.sql")

def input():
    menus = db.query(Menu).all();
    ms = {}
    price = {}
    for menu in menus:
        ms[menu.name] = menu.id;
        price[menu.name] = menu.price
        wb = load_workbook(filename='../backup.xlsx',read_only = True)
        ws = wb['입출금관리']
        a = lambda x: x>0
        takeout = lambda x: x=="배달"
        for row in ws.iter_rows(row_offset=1):
            date = str(row[0].value)+' '+str(row[2].value)+':00'
            totalprice = row[6]
            order = Order(date,totalprice)
            db.add(order)
            count_twice = get_sign(str(row[13].value),"곱배기추가")
            count_curry = get_sign(str(row[13].value),"카레추가")
            ordermenus = str(row[13].value).split(",")
            for o in ordermenus:
                if int(row[8].value) == 0:
                    pay = 2
                elif int(row[9].value) ==0:
                    pay = 1
                else:
                    pay = 4
                with open('notmatchedmenu.csv','wb') as f:
                    fieldnames = ['menus','something']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    if o.endswith(")"):
                        bef,m,aft = order.partition("(")
                        bef,m,aft = aft.partition(")")
                        for i in range(bef):
                            if bef in ms:
                                ordermenu = OrderMenu(menu=ms[bef],order=order, pay=pay,curry=a(count_curry),
                                twice=a(count_twice),takeout=takeout(str(row[3].value)))
                                count_twice = count_twice - 1
                                count_curry = count_curry - 1
                                db.add(ordermenu)
                            else:
                                writer = csv.writer(f)
                                writer.writerow({'menus':bef, "something":0})

                    else:
                        if o in ms:
                            ordermenu = OrderMenu(menu=ms[o],order=order,pay=pay,curry=a(count_curry),
                            twice=(count_twice),takeout=takeout(str(row[3].value)))
                            count_twice = count_twice - 1
                            count_curry = count_curry - 1 
                            db.add(ordermenu)
                            db.commit()
                        else:
                            writer = csv.writer(f)
                            writer.writerow({'menus':o, "something":0})

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

