class Parallel8255:
    def __init__(self):
        self.control_register = 0x00  # 控制寄存器
        self.port_a = 0x00  # 端口A
        self.port_b = 0x00  # 端口B
        self.port_c = 0x00  # 端口C

    def write_control(self, value):
        """写入控制寄存器以设置模式"""
        self.control_register = value
        print(f"Control register set to: {bin(value)}")

    def write_port(self, port, value):
        """向指定端口写入数据"""
        if port == 'A':
            self.port_a = value
            print(f"Port A written with: {hex(value)}")
        elif port == 'B':
            self.port_b = value
            print(f"Port B written with: {hex(value)}")
        elif port == 'C':
            self.port_c = value
            print(f"Port C written with: {hex(value)}")
        else:
            raise ValueError("Invalid port")

    def read_port(self, port):
        """从指定端口读取数据"""
        if port == 'A':
            print(f"Port A read: {hex(self.port_a)}")
            return self.port_a
        elif port == 'B':
            print(f"Port B read: {hex(self.port_b)}")
            return self.port_b
        elif port == 'C':
            print(f"Port C read: {hex(self.port_c)}")
            return self.port_c
        else:
            raise ValueError("Invalid port")
