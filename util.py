

import os
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
