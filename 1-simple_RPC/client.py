import threading
import time

from services import *



#创建与服务器的连接


#进行调用
channel = Channel('localhost', 8000)
def divide(i):
    try:
        time.sleep(1)
        # chuangjian 用于RPC调用的工具
        stub = ClientStub(channel)
        val = stub.divide(i*200,100)
    except InvalidOperation as e:
        print(e.message)
    else:
        print(val)
for i in range(10):
    threading.Thread(target=divide, args=(i,)).start()

