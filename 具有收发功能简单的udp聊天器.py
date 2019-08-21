import socket


def udp_send(udp_socket):
    """获取键盘内容并发送"""
    ip = input("请输入对方IP：")
    port = int(input("请输入对方端口号"))
    send_msg = input("请输入要发送的内容：")
    udp_socket.sendto(send_msg.encode('gbk'), (ip, port))


def udp_recv(udp_socket):
    """接受对方发送的内容并显示"""
    recv_msg = udp_socket.recvfrom(1024)
    print(recv_msg[0].decode('gbk'))


def main():
    """提示用户选择功能"""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(('', 1888))
    while True:
        print("_" * 40)
        print("1:发送消息")
        print("2.接收消息")
        num = input("请输入要选择的功能：")
        if num == '1':
            udp_send(udp_socket)
        elif num == '2':
            udp_recv(udp_socket)
        else:
            print("输入有误，清重新输入。")


if __name__ == '__main__':
    main()
