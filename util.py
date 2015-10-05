__author__ = 'ohyongtaek'

import os
def print_statement(order):
    output = u''
    output += u'상 호 명:  송호성 쉐프의 돈까스\n'
    output += u'등록번호: 134-31-16828\n'
    output += u'\\x1bm'
    f1 = open('./test','w+')
    print(output,file = f1)
    f1.close()
    os.system('lpr test')