__author__ = 'ohyongtaek'

import os
def print_statement(order):
    output = ''
    output +='상 호 명:  송호성 쉐프의 돈까스\n'
    output +='등록번호: 134-31-16828\n'
    output +='\\x1bm'
    f1 = open('./test','w+')
    print >> f1, output
    f1.close()
    os.system('lpr test')