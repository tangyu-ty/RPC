import struct
import threading
from io import BytesIO
import socket


class InvalidOperation(Exception):
    def __init__(self, message=None):
        self.message = message or 'Invalid operation'


class MethodProtocol(object):
    """
    解读方法名字
    """

    def __init__(self, connection):
        self.conn = connection

    def _read_all(self, size):
        """
        解码读取二进制数据
        :param size: 数据的大小
        :return: 返回字节
        """

        # self.conn
        # 读取二进制
        # socket.recv(4) =>?4
        # BytesIO.read
        if isinstance(self.conn, BytesIO):
            buff = self.conn.read(size)
            return buff
        else:
            # socket
            # recv函数仅仅是copy数据，真正的接收数据是协议来完成的
            # 注意协议接收到的数据可能大于buf的长度，所以需要多次recv函数将socket中的buf中。
            have = 0
            buff = b''
            while have < size:
                chunk = self.conn.recv(size - have)
                buff += chunk
                have += len(chunk)

                if len(chunk) == 0:
                    # 表示客户端socket关闭了
                    raise EOFError()
            return buff

    def get_method_name(self):
        """
        提供方法名
        :return: str 方法名
        """

        # 读取字符串长度
        buff = self._read_all(4)
        length = struct.unpack('!I', buff)[0]

        # 读取字符串

        buff = self._read_all(length)
        name = buff.decode()
        return name


class DivideProtocol(object):
    """
    divide过程消息协议转换
    """

    def args_encode(self, num1, num2=1):
        """
        将原始调用请求参数转换打包成二进制消息数据
        :param num1: int
        :param num2: int
        :return: bytes 二进制消息数据
        """
        name = 'divide'

        # 处理方法的名字，字符串
        # 处理字符串的长度
        buff = struct.pack('!I', len(name))

        # 处理字符
        name.encode()
        buff = buff + name.encode()

        # 处理参数1
        buff2 = struct.pack('!B', 1)
        buff2 = buff2 + struct.pack('!i', num1)

        # 处理参数2
        if num2 != 1:
            buff2 = buff2 + struct.pack('!B', 2)
            buff2 = buff2 + struct.pack('!i', num2)

        # 处理消息长度，边界设定，统计buff2的长度
        length = len(buff2)

        # 填充长度到4个字节
        buff = buff + struct.pack('!I', length)
        return buff + buff2

    def _read_all(self, size):
        """
        解码读取二进制数据
        :param size: 数据的大小
        :return: 返回字节
        """

        # self.conn
        # 读取二进制
        # socket.recv(4) =>?4
        # BytesIO.read
        if isinstance(self.conn, BytesIO):
            buff = self.conn.read(size)
            return buff
        else:
            # socket
            # recv函数仅仅是copy数据，真正的接收数据是协议来完成的
            # 注意协议接收到的数据可能大于buf的长度，所以需要多次recv函数将socket中的buf中。
            have = 0
            buff = b''
            while have < size:
                chunk = self.conn.recv(size - have)
                buff += chunk
                have += len(chunk)

                if len(chunk) == 0:
                    # 表示客户端socket关闭了
                    raise EOFError()
            return buff

    def args_decode(self, connection):
        """
        接受调用请求消息数据并精细解析
        :param connection: 连接对象 socket BytesIO
        :return: dict 包含解析后的参数
        """

        # 通过参数类型读取字节
        param_len_map = {
            1: 4,
            2: 4
        }
        # 参数格式
        param_fmt_map = {
            1: '!i',
            2: '!i'
        }

        # 参数名字,节约网络消息传输数据量
        param_name_map = {
            1: 'num1',
            2: 'num2'
        }

        # return字典
        args = {}

        self.conn = connection

        # 处理消息边界

        # 读取二进制数据
        # socket.recv(4) => ?4
        # BytesIO.read

        buff = self._read_all(4)
        # 将二进制转换为python类型
        length = struct.unpack('!I', buff)[0]

        # 已经读取处理的字节数
        have = 0

        # 处理第一个参数
        # 处理序号
        buff = self._read_all(1)
        have += 1
        param_seq = struct.unpack('!B', buff)[0]

        # 处理参数值
        param_len = param_len_map[param_seq]
        buff = self._read_all(param_len)
        have += param_len
        param_fmt = param_fmt_map[param_seq]
        param = struct.unpack(param_fmt, buff)[0]
        param_name = param_name_map[param_seq]
        args[param_name] = param
        if have >= length:
            return args
        # 处理第二个参数
        # 处理序号

        buff = self._read_all(1)
        param_seq = struct.unpack('!B', buff)[0]

        # 处理参数值
        param_len = param_len_map[param_seq]
        buff = self._read_all(param_len)
        param_fmt = param_fmt_map[param_seq]
        param = struct.unpack(param_fmt, buff)[0]
        param_name = param_name_map[param_seq]
        args[param_name] = param
        return args

    def result_encode(self, result):
        """
        将原始结果数据转换为消息协议二进制数据
        :param result: 原始的结果数据 float、InvalidOperation
        :return: bytes 消息协议二进制数据
        """

        # 正常的情况

        if isinstance(result, float): \
                # 处理正常返回值类型
            buff = struct.pack('!B', 1)
            buff += struct.pack('!f', result)
            return buff
        # 异常的情况
        else:
            # 处理异常返回值类型
            buff = struct.pack('!B', 2)
            length = len(result.message)
            # 处理字符串长度
            buff += struct.pack('!I', length)
            buff += result.message.encode('utf-8')
            return buff

    def result_decode(self, connection):
        """
        将返回值消息数据转为原始返回值
        :param connection: socket BytesIO
        :return: float InvalidOperation对象
        """
        self.conn = connection  # self._read_all(1)需要self.conn
        # 处理返回值类型
        buff = self._read_all(1)
        result_type = struct.unpack('!B', buff)[0]
        if result_type == 1:
            # 正常
            # 读取float数据
            buff = self._read_all(4)
            val = struct.unpack('!f', buff)[0]
            return val
        elif result_type == 2:
            # 异常
            # 读取字符串长度
            # 读取字符串
            buff = self._read_all(4)
            length = struct.unpack('!I', buff)[0]
            buff = self._read_all(length)
            message = buff.decode('utf-8')
            return InvalidOperation(message)


class Channel(object):
    """
    用于客户端简历网络连接
    """

    def __init__(self, host, port):
        """

        :param host:服务器地址
        :param port: 服务器端口号
        """
        self.host = host
        self.port = port

    def get_connection(self):
        """
        获取连接对象
        :return: 与服务器通讯的socket
        """

        # AF_INET ipv4
        # SOCK_STREAM TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        return sock


class Server(object):
    """
    PRC服务器
    """

    def __init__(self, host, port, handlers):
        # 创建socket工具对象
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置socket 重用地址
        # SOL_SOCKET：sockt的本身的级别、SO_REUSEADDR：重用地址
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind((host, port))
        self.host = host
        self.port = port
        self.sock = sock
        self.handlers = handlers

    def serve(self):
        """
        开启服务器运行，提供RPC服务
        :return:
        """

        # 开启服务器的监听，等待客户端的连接请求
        self.sock.listen(128)
        print("服务器开启监听")
        # 接受客户端的连接请求
        while True:
            client_sock, client_addr = self.sock.accept()
            print('与客户端%s建立了连接' % str(client_addr))

            # 交给ServerStub，完成客户端的具体RPC调用请求
            stub = ServerStub(client_sock, self.handlers)
            try:
                while True:
                    stub.process()
            except EOFError:
                # 表示客户端关闭了连接
                print("客户端关闭了连接")
                client_sock.close()


class ThreadServer(Server):
    """
    多线程PRC服务器
    """

    def serve(self):
        """
        开启服务器运行，提供RPC服务
        :return:
        """

        # 开启服务器的监听，等待客户端的连接请求
        self.sock.listen(128)
        print("服务器开启监听")
        # 接受客户端的连接请求
        while True:
            client_sock, client_addr = self.sock.accept()
            print('与客户端%s建立了连接' % str(client_addr))
            # 创建子线程处理客户端
            thread = threading.Thread(target=self.handle, args=(client_sock,))
            thread.start()
    def handle(self, client_sock):
        """
        子线程调用的方法，用户处理一个客户端的请求
        :return:
        """

        # 交给ServerStub，完成客户端的具体RPC调用请求
        stub = ServerStub(client_sock, self.handlers)
        try:
            while True:
                stub.process()
        except EOFError:
            # 表示客户端关闭了连接
            print("客户端关闭了连接")
            client_sock.close()



class ClientStub(object):
    """
    用来帮助客户端能完成远程过程调用 RPC调用
    stub = ClientStub()
    stub.divide()
    """

    def __init__(self, channel):
        self.channel = channel
        self.conn = self.channel.get_connection()

    def divide(self, num1, num2=1):
        # 将调用的参数打包成消息协议的数据
        proto = DivideProtocol()
        args = proto.args_encode(num1, num2)

        # 将消息数据通过网络发送给服务器

        self.conn.sendall(args)

        # 接受服务器返回的返回值消息数据，并进行解析

        result = proto.result_decode(self.conn)

        # 将结果值(正常float 或者异常InvalidOperation)返回给客户端

        if isinstance(result, float):
            # 正常情况
            return result
        else:
            raise result

        # def add(self):
        #     pass


class ServerStub(object):
    """
    帮助服务器完成远程过程调用
    """

    def __init__(self, connection, handlers):
        """

        :param connection: 与客户端的连接
        :param handlers: 真正本地被调用的方法
        class Handler(object):
            def divide(self, num1, num2=1):
                pass
            @staticmethod
            def add(self, num1, num2=1):
                pass
        """
        self.conn = connection
        self.method_proto = MethodProtocol(self.conn)
        self.process_map = {
            'divide': self._process_divide
        }
        self.handlers = handlers

    def process(self):
        """
        当服务端接受了一个客户端的连接，建立好连接后进行远端调用
        :return:
        """

        # 接受消息数据，并解析方法的名字
        name = self.method_proto.get_method_name()
        # 根据解析获得的方法（过程）名，调用相应的过程协议，接受并解析消息数据。
        self.process_map[name]()

    def _process_divide(self):
        # 创建用于除法过程的调用参数协议数据解析的工具
        proto = DivideProtocol()
        # 解析调用参数消息数据
        args = proto.args_decode(self.conn)

        # 除法的本地调用
        try:
            val = self.handlers.divide(**args)
        except InvalidOperation as e:
            ret_message = proto.result_encode(e)
        else:
            ret_message = proto.result_encode(val)
        self.conn.sendall(ret_message)
        # 将本地调用的返回值打包成消息协议的数据，通过网络返回给客户端

    def _process_add(self):
        pass
