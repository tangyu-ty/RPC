from services import InvalidOperation, Server, ThreadServer


class Handlers(object):
    @staticmethod
    def divide(num1, num2=1):
        if num2 == 0:
            raise InvalidOperation("itcast")
        return num1 / num2


if __name__ == '__main__':
    _server = ThreadServer('127.0.0.1', 8000, Handlers)
    _server.server()
