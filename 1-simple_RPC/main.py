# 按间距中的绿色按钮以运行脚本。
from io import BytesIO
from services import DivideProtocol
from services import MethodProtocol

if __name__ == '__main__':
    # 构造消息数据
    proto = DivideProtocol()
    message = proto.args_encode(200, 100)
    conn = BytesIO()
    conn.write(message)  # 读取数据
    conn.seek(0)
    # 解析消息数据

    method_proto = MethodProtocol(conn)
    name = method_proto.get_method_name()
    print(name)

    args=proto.args_decode(conn)
    print(args)