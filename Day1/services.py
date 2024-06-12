import struct
from io import BytesIO


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

        # todo 处理方法名

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


        #正常的情况

        if isinstance(result,float):
            pass
        #异常的情况
        else:
            pass