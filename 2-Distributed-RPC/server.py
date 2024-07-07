import sys

from services import InvalidOperation, Server, ThreadServer
from DTservices import DTServices


class Handlers(object):
    @staticmethod
    def divide(num1, num2=1):
        if num2 == 0:
            raise InvalidOperation("itcast")
        return num1 / num2


if __name__ == '__main__':
    # _server = DTServices('127.0.0.1', 8000, Handlers)
    # _server.serve()

    # 从启动命令中提取服务器的ip地址和端口
    host = sys.argv[1]
    port = int(sys.argv[2])

    _server = DTServices(host, port, Handlers)
    _server.serve()
