# class Parallel8255:
#     def __init__(self):
#         self.control_register = 0x00  # 控制寄存器
#         self.port_a = 0x00  # 端口A
#         self.port_b = 0x00  # 端口B
#         self.port_c = 0x00  # 端口C
#
#     def write_control(self, value):
#         """写入控制寄存器以设置模式"""
#         self.control_register = value
#         print(f"Control register set to: {bin(value)}")
#
#     def write_port(self, port, value):
#         """向指定端口写入数据"""
#         if port == 'A':
#             self.port_a = value
#             print(f"Port A written with: {hex(value)}")
#         elif port == 'B':
#             self.port_b = value
#             print(f"Port B written with: {hex(value)}")
#         elif port == 'C':
#             self.port_c = value
#             print(f"Port C written with: {hex(value)}")
#         else:
#             raise ValueError("Invalid port")
#
#     def read_port(self, port):
#         """从指定端口读取数据"""
#         if port == 'A':
#             print(f"Port A read: {hex(self.port_a)}")
#             return self.port_a
#         elif port == 'B':
#             print(f"Port B read: {hex(self.port_b)}")
#             return self.port_b
#         elif port == 'C':
#             print(f"Port C read: {hex(self.port_c)}")
#             return self.port_c
#         else:
#             raise ValueError("Invalid port")
class Parallel8255:
    def __init__(self):
        # 内部寄存器
        self.control_register = 0x00  # 控制寄存器
        self.port_a = 0x00  # 端口A
        self.port_b = 0x00  # 端口B
        self.port_c = 0x00  # 端口C

        # 模拟引脚
        self.data_lines = [0] * 8  # 数据线 D7~D0
        self.control_lines = {'RD': True, 'WR': True, 'CS': True, 'RESET': False}  # 控制线，默认未激活
        self.address_lines = [0, 0]  # 地址线 A1, A0

    def reset(self):
        """复位芯片，清除所有寄存器数据"""
        self.control_register = 0x00
        self.port_a = 0x00
        self.port_b = 0x00
        self.port_c = 0x00
        self.control_lines['RESET'] = True
        print("Chip reset. All ports set to 0.")

    def set_address(self, a1, a0):
        """设置地址线 A1/A0，用于选择端口"""
        self.address_lines = [a1, a0]
        print(f"Address lines set to: A1={a1}, A0={a0}")

    def set_control_lines(self, rd, wr, cs):
        """设置控制线 RD, WR, CS"""
        self.control_lines['RD'] = rd
        self.control_lines['WR'] = wr
        self.control_lines['CS'] = cs
        print(f"Control lines set to: RD={rd}, WR={wr}, CS={cs}")

    def set_data_lines(self, data):
        """设置数据线值 D7~D0"""
        self.data_lines = [int(bit) for bit in bin(data)[2:].zfill(8)]
        print(f"Data lines set to: {self.data_lines}")

    def get_data_lines(self):
        """获取数据线值 D7~D0"""
        return int("".join(map(str, self.data_lines)), 2)

    def write(self, data):
        """向指定端口写入数据"""
        if self.control_lines['CS'] == False and self.control_lines['WR'] == False:  # 检查片选和写使能信号
            self.set_data_lines(data)
            address = self.address_lines
            if address == [0, 0]:  # 选择端口A
                self.port_a = self.get_data_lines()
                print(f"Data written to Port A: {hex(self.port_a)}")
            elif address == [0, 1]:  # 选择端口B
                self.port_b = self.get_data_lines()
                print(f"Data written to Port B: {hex(self.port_b)}")
            elif address == [1, 0]:  # 选择端口C
                self.port_c = self.get_data_lines()
                print(f"Data written to Port C: {hex(self.port_c)}")
            elif address == [1, 1]:  # 控制寄存器
                self.control_register = self.get_data_lines()
                print(f"Data written to Control Register: {hex(self.control_register)}")
            else:
                raise ValueError("Invalid address lines.")
        else:
            print("Write operation failed: Control signals not valid.")

    def read(self):
        """从指定端口读取数据"""
        if self.control_lines['CS'] == False and self.control_lines['RD'] == False:  # 检查片选和读使能信号
            address = self.address_lines
            if address == [0, 0]:  # 选择端口A
                data = self.port_a
                self.set_data_lines(data)
                print(f"Data read from Port A: {hex(data)}")
            elif address == [0, 1]:  # 选择端口B
                data = self.port_b
                self.set_data_lines(data)
                print(f"Data read from Port B: {hex(data)}")
            elif address == [1, 0]:  # 选择端口C
                data = self.port_c
                self.set_data_lines(data)
                print(f"Data read from Port C: {hex(data)}")
            elif address == [1, 1]:  # 控制寄存器
                data = self.control_register
                self.set_data_lines(data)
                print(f"Data read from Control Register: {hex(data)}")
            else:
                raise ValueError("Invalid address lines.")
        else:
            print("Read operation failed: Control signals not valid.")

    def configure_ports(self):
        """根据控制寄存器配置端口工作模式"""
        # 假设控制寄存器的低3位表示端口A、B、C的工作模式
        mode_a = (self.control_register >> 0) & 0x03
        mode_b = (self.control_register >> 2) & 0x03
        mode_c = (self.control_register >> 4) & 0x03

        self.port_mode('A', mode_a)
        self.port_mode('B', mode_b)
        self.port_mode('C', mode_c)

    def port_mode(self, port, mode):
        """设置端口工作模式：0=输入，1=输出"""
        if port == 'A':
            if mode == 0:
                print("Port A set to Input mode.")
            elif mode == 1:
                print("Port A set to Output mode.")
            else:
                raise ValueError("Invalid mode for port A")
        elif port == 'B':
            if mode == 0:
                print("Port B set to Input mode.")
            elif mode == 1:
                print("Port B set to Output mode.")
            else:
                raise ValueError("Invalid mode for port B")
        elif port == 'C':
            if mode == 0:
                print("Port C set to Input mode.")
            elif mode == 1:
                print("Port C set to Output mode.")
            else:
                raise ValueError("Invalid mode for port C")
        else:
            raise ValueError("Invalid port")

# # 创建芯片实例
# chip = Parallel8255()
#
# # 复位芯片
# chip.reset()
#
# # 设置地址线选择端口A
# chip.set_address(0, 0)
#
# # 设置控制线，片选有效，写使能低电平
# chip.set_control_lines(rd=True, wr=False, cs=False)
#
# # 向端口A写入数据
# chip.write(0x5A)
#
# # 设置控制线，片选有效，读使能低电平
# chip.set_control_lines(rd=False, wr=True, cs=False)
#
# # 从端口A读取数据
# chip.read()
