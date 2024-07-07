import json
import random
import threading
import time

from kazoo.client import KazooClient
import socket
from services import ThreadServer


class DTServices(ThreadServer):
    """
    Distributed Thread => DT
    """

    # 重写服务，将注册zookeeper写入到服务中
    def serve(self):
        """
        开启服务器运行，提供RPC服务
        :return:
        """

        # 开启服务器的监听，等待客户端的连接请求
        self.sock.listen(128)
        print("服务器开启监听")

        # 注册到zookeeper
        self.register_zookeeper()

        # 接受客户端的连接请求
        while True:
            client_sock, client_addr = self.sock.accept()
            print('与客户端%s建立了连接' % str(client_addr))
            # 创建子线程处理客户端
            thread = threading.Thread(target=self.handle, args=(client_sock,))
            thread.start()

    def register_zookeeper(self):
        """
        注册在zookeeper中心注册本服务器的地址信息
        :return:
        """
        # 创建zookeeper客户端kazoo
        zk = KazooClient(hosts='127.0.0.1:2181')
        # 建立连接
        zk.start()
        # zookeeper中创建节点保存数据
        zk.ensure_path('rpc')
        data = json.dumps({'host': self.host, 'port': self.port})
        zk.create('rpc/server', data.encode("utf-8"), ephemeral=True, sequence=True)


class DTChannel(object):
    """
    支持分布式的zookeeper得PRC客户端通讯连接工具
    """

    def __init__(self):
        # 创建Kazoo对象，连接zookeeper，获取信息
        self.zk = KazooClient(hosts='127.0.0.1:2181')
        self.zk.start()
        self._servers = []
        self._get_servers()

    def _get_servers(self, event=None):
        """
        从zookeeper中获取所有可用的RPC服务器的地址信息
        :return:
        """
        self._servers = []
        # 从zookeeper中获取/rpc节点下所有可用的服务器节点
        servers = self.zk.get_children('/rpc', watch=self._get_server)  # 单次回调，实际上是一个循环。

        for server in servers:
            addr_data = self.zk.get('/rpc/' + server)[0]
            addr = json.loads(addr_data)
            self._servers.append(addr)

    def _get_server(self):
        """
        从可用的服务器列表中选出一台服务器
        :return: {"host": host, "port": port}
        """
        return random.choice(self._servers)

    def get_connection(self):
        """
        提供一个具体的与RPC服务器的连接socket
        :return:
        """
        while True: #循环的效率比递归高很多，不用开辟额外的栈空间
            addr = self._get_server()
            print(addr)
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 流式协议
                sock.connect((addr['host'], addr['port']))
            except ConnectionRefusedError:
                time.sleep(1)
                continue
            else:
                return sock
