import random
import time

from services import *

from DTservices import DTChannel

#创建与服务器的连接


#进行调用
channel = DTChannel()
def divide(i):
    for i in range(10):
        try:
            time.sleep(1)
            # chuangjian 用于RPC调用的工具
            stub = ClientStub(channel)
            val = stub.divide(i*200,100)
        except InvalidOperation as e:
            print(e.message)
        else:
            print(val)
        time.sleep(random.randint(0,2))
for i in range(2):
    threading.Thread(target=divide, args=(i,)).start()
