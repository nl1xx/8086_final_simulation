from Peripheral import Peripheral
from PTimer8235 import Timer8235
from Parallel8255 import Parallel8255

peripheral = Peripheral()
timer = Timer8235()
parallel8255 = Parallel8255()

class BIU:
    def __init__(self, memory, instructions):
        self.memory = memory
        self.instructions = instructions  # 将指令列表传递给BIU

    def fetch_instruction(self, ip):
        # 确保 IP 寄存器的值在有效范围内
        if ip < len(self.instructions):
            return self.instructions[ip]
        else:
            return 'HLT'  # 如果 IP 超出范围，返回 HLT 指令以停止执行


class EU:
    def __init__(self):
        self.registers = {
            'AX': 0, 'BX': 0, 'CX': 0, 'DX': 0,
            'SP': 0, 'BP': 0, 'SI': 0, 'DI': 0,
            'IP': 0, 'CS': 0, 'DS': 0, 'ES': 0, 'SS': 0
        }
        self.status_flags = {'CF': 0, 'PF': 0, 'ZF': 0, 'SF': 0, 'OF': 0, 'DF': 0, 'IF': 0}
        self.call_stack = []
        self.memory = None
        self.procedures = {}  # 存储过程定义的入口点
        self.data_segment = {}  # 存储数据定义
        self.labels = {}  # 存储标签位置
        self.current_segment = 'CODE'  # 初始设置为代码段
        self.comments = []  # 用于存储解析过程中遇到的注释
        self.timer = timer
        self.parallel_interface = parallel8255

    def set_memory(self, memory):
        self.memory = memory

    def print_reg(self):
        print(f"寄存器状态: {self.registers}")
        print("--------------------")

    def print_flags(self):
        print(f"标志寄存器状态: {self.status_flags}")

    def alu(self, opcode, a, b=0, cf=0):
        res = 0
        if opcode == 'ADD':
            res = (a + b + cf) & 0xFFFF
            self.status_flags['OF'] = 1 if ((a > 0 > res and b > 0) or (a < 0 < res and b < 0)) else 0
        elif opcode == 'SUB':
            res = a - b - cf
            if res < 0:
                self.status_flags['CF'] = 1
                res += 0x10000
            self.status_flags['OF'] = 1 if ((a < 0 < b and res > 0) or (a > 0 > b and res < 0)) else 0
        elif opcode == 'MUL':
            res = (a * b) & 0xFFFF
        elif opcode == 'DIV':
            res = a // b if b != 0 else 0
        elif opcode in ['AND', 'OR', 'XOR', 'NOT']:
            if opcode == 'AND':
                res = a & b
            elif opcode == 'OR':
                res = a | b
            elif opcode == 'XOR':
                res = a ^ b
            elif opcode == 'NOT':
                res = ~a & 0xFFFF

        # Update flags
        self.status_flags['ZF'] = 1 if res == 0 else 0
        self.status_flags['SF'] = 1 if res & 0x8000 else 0
        return res

    def parse_data_segment(self, instructions):
        data_start = False
        for instruction in instructions:
            instruction = instruction.strip()
            if instruction.startswith(".DATA"):
                data_start = True
                continue
            if instruction.startswith(".CODE") or instruction.startswith(".STACK"):
                data_start = False
                continue
            if data_start:
                parts = instruction.split()
                opcode = parts[0]
                if opcode in ["DB", "DW", "DD"]:
                    label = parts[1].rstrip(":")
                    value = int(parts[2], 0)
                    self.data_segment[label] = value

    def get_value(self, operand):
        # 立即数寻址
        if operand.isdigit() or (operand[0] == '-' and operand[1:].isdigit()):
            return int(operand)

        # 寄存器寻址
        if operand in self.registers:
            return self.registers[operand]

        # 标签寻址
        if operand in self.data_segment:
            return self.data_segment[operand]  # 从数据段获取标签对应的值

        # 直接寻址（[address]）
        if operand.startswith('[') and operand.endswith(']'):
            operand = operand[1:-1]  # 去除括号
            if operand.isdigit():
                addr = int(operand)
                return self.memory[addr]
            else:
                addr = self.registers[operand]
                return self.memory[addr]

        raise ValueError(f"无法解析操作数: {operand}")

    def write_value(self, operand, value):
        # 寄存器寻址
        if operand in self.registers:
            self.registers[operand] = value
        # 直接寻址（[address]）
        elif operand.startswith('[') and operand.endswith(']'):
            operand = operand[1:-1]  # 去除括号
            # 检查是否为纯数字地址
            if operand.isdigit():
                addr = int(operand)
                self.memory[addr] = value
            else:
                # 处理寄存器间接寻址
                addr = self.registers[operand]
                self.memory[addr] = value
        # 基址加变址寻址
        elif '+' in operand:
            base, index = operand[1:-1].split('+')
            addr = self.registers[base] + self.registers[index]
            self.memory[addr] = value
        # 相对寻址
        elif operand.startswith('[') and operand[1:3] == 'IP':
            offset = int(operand[4:-1])
            addr = self.registers['IP'] + offset
            self.memory[addr] = value
        else:
            raise ValueError(f"无效的操作数: {operand}")

    def execute_instruction(self, instruction):
        instruction = instruction.split(";")[0].strip()  # 移除注释
        parts = instruction.split()

        if not parts:
            return True  # 忽略空行和只有注释的行

        opcode = parts[0]

        # 段定义伪指令
        if opcode == ".CODE":
            print("切换到代码段")
            self.current_segment = 'CODE'
        elif opcode == ".DATA":
            print("切换到数据段")
            self.current_segment = 'DATA'
        elif opcode == ".STACK":
            print("切换到堆栈段")
            self.current_segment = 'STACK'

        # 数据定义伪指令
        elif opcode == "DB":  # 定义字节数据
            label = parts[1].rstrip(':')
            value = int(parts[2], 0)
            self.data_segment[label] = value
            print(f"定义字节数据: {label} = {value}")
        elif opcode == "DW":  # 定义字数据
            label = parts[1].rstrip(':')
            value = int(parts[2], 0)
            self.data_segment[label] = value
            print(f"定义字数据: {label} = {value}")
        elif opcode == "DD":  # 定义双字数据
            label = parts[1].rstrip(':')
            value = int(parts[2], 0)
            self.data_segment[label] = value
            print(f"定义双字数据: {label} = {value}")

        # 过程定义伪指令
        elif opcode == "PROC":  # 定义过程（函数）
            label = parts[1]
            self.procedures[label] = self.registers['IP']
            print(f"过程 {label} 定义在位置 {self.registers['IP']}")
        elif opcode == "ENDP":  # 结束过程
            print("过程结束")

        # 标签处理
        elif ':' in opcode:  # 处理标签
            label = opcode.rstrip(':')
            self.labels[label] = self.registers['IP']
            print(f"标签 {label} 定义在位置 {self.registers['IP']}")

        if opcode == "VOICE":
            voice_code = parts[1]
            voice_map = {
                "01": {"device": "LED1", "state": 1},
                "02": {"device": "LED1", "state": 0},
                "03": {"device": "LED2", "state": 1},
                "04": {"device": "LED2", "state": 0},
                "05": {"device": "Fan1", "state": 1},
                "06": {"device": "Fan1", "state": 0},
                "07": {"device": "Fan2", "state": 1},
                "08": {"device": "Fan2", "state": 0},
                "09": {"device": "LED3", "state": 1},
                "10": {"device": "LED3", "state": 0},
                "11": {"device": "Fan3", "state": 1},
                "12": {"device": "Fan3", "state": 0},
            }
            if voice_code in voice_map:
                action = voice_map[voice_code]
                peripheral.control_device(action["device"], action["state"])
                peripheral.update_display(f"{action['device']} {'ON' if action['state'] else 'OFF'}")
            else:
                peripheral.update_display("Unknown Command")

        elif opcode == "STATUS":
            device = parts[1]
            status = peripheral.query_status(device)
            peripheral.update_display(status)

        if opcode == "CONFIG_TIMER":
            mode = int(parts[1])
            initial_value = int(parts[2])
            self.timer.configure(mode, initial_value)
        elif opcode == "START_TIMER":
            self.timer.start()
        elif opcode == "STOP_TIMER":
            self.timer.stop()
        elif opcode == "TICK_TIMER":
            self.timer.tick()
            if self.timer.counter_register == 3:
                peripheral.control_device("LED3", 1)
                print("LED3 turned ON")
                print("Fan3 turned OFF")
            elif self.timer.counter_register == 5:
                peripheral.control_device("Fan3", 1)
                print("Fan3 turned ON")
            elif self.timer.counter_register == 2:
                print("LED3 turned OFF")

        if opcode == "WRITE_CTRL":
            value = int(parts[1], 16)  # 将十六进制字符串转换为整数
            self.parallel_interface.set_address(1, 1)  # 地址线选择控制寄存器
            self.parallel_interface.set_control_lines(rd=True, wr=False, cs=False)  # 设置写操作
            self.parallel_interface.write(value)  # 写入控制寄存器的值

        elif opcode == "WRITE_PORT":
            port = parts[1]
            value = int(parts[2], 16)

            if port == "A":
                self.parallel_interface.set_address(0, 0)  # 地址线选择端口A
            elif port == "B":
                self.parallel_interface.set_address(0, 1)  # 地址线选择端口B
            elif port == "C":
                self.parallel_interface.set_address(1, 0)  # 地址线选择端口C
            else:
                raise ValueError("Invalid port specified")

            self.parallel_interface.set_control_lines(rd=True, wr=False, cs=False)  # 设置写操作
            self.parallel_interface.write(value)  # 写入端口值

        elif opcode == "READ_PORT":
            # 从指定端口读取数据
            port = parts[1]

            if port == "A":
                self.parallel_interface.set_address(0, 0)  # 地址线选择端口A
            elif port == "B":
                self.parallel_interface.set_address(0, 1)  # 地址线选择端口B
            elif port == "C":
                self.parallel_interface.set_address(1, 0)  # 地址线选择端口C
            else:
                raise ValueError("Invalid port specified")

            self.parallel_interface.set_control_lines(rd=False, wr=True, cs=False)  # 设置读操作
            self.parallel_interface.read()  # 读取端口值

        # 其他普通指令（如MOV、ADD等），这里省略常规指令的执行部分
        else:
            parts = instruction.split()
            opcode = parts[0]
            if opcode == "HLT":
                print("停止执行")
                return False
            elif opcode == "MOV":
                dest, src = parts[1], parts[2]
                self.write_value(dest, self.get_value(src))
            elif opcode == "ADD":
                dest, src = parts[1], parts[2]
                result = self.alu('ADD', self.get_value(dest), self.get_value(src))
                self.write_value(dest, result)
            elif opcode == "SUB":
                dest, src = parts[1], parts[2]
                result = self.alu('SUB', self.get_value(dest), self.get_value(src))
                self.write_value(dest, result)
            elif opcode == "MUL":
                dest, src = parts[1], parts[2]
                result = self.alu('MUL', self.get_value(dest), self.get_value(src))
                self.write_value(dest, result)
            elif opcode == "DIV":
                dest, src = parts[1], parts[2]
                result = self.alu('DIV', self.get_value(dest), self.get_value(src))
                self.write_value(dest, result)
            elif opcode in ["AND", "OR", "XOR", "NOT"]:
                dest = parts[1]
                if opcode == "NOT":
                    result = self.alu('NOT', self.get_value(dest))
                else:
                    src = parts[2]
                    result = self.alu(opcode, self.get_value(dest), self.get_value(src))
                self.write_value(dest, result)
            elif opcode == "PUSH":
                value = self.get_value(parts[1])
                self.call_stack.append(value)
            elif opcode == "POP":
                if self.call_stack:
                    self.write_value(parts[1], self.call_stack.pop())
                else:
                    print("栈空，无法弹出")
            elif opcode == "JMP":
                target = self.get_value(parts[1])
                self.registers['IP'] = target - 1  # 减去1是因为在执行完当前指令后IP会自动加1
            elif opcode == "CALL":
                self.call_stack.append(self.registers['IP'] + 1)  # Push the next instruction address
                target = self.get_value(parts[1])
                self.registers['IP'] = target - 1  # 同上
            elif opcode == "RET":
                if self.call_stack:
                    self.registers['IP'] = self.call_stack.pop()
                else:
                    print("栈空，无法返回")

            elif opcode == "MOVSB":
                self.movsb()
            elif opcode == "MOVSW":
                self.movsw()
            elif opcode == "CMPSB":
                self.cmpsb()
            elif opcode == "CMPSW":
                self.cmpsw()
            elif opcode == "STC":
                self.stc()
            elif opcode == "CLC":
                self.clc()

        self.print_flags()
        self.print_reg()
        return True

    def movsb(self):
        """Move byte from source index (SI) to destination index (DI) and update indices."""
        byte = self.memory[self.registers['SI']]
        self.memory[self.registers['DI']] = byte
        # Update SI and DI based on the direction flag
        if self.status_flags['DF'] == 0:  # Increment
            self.registers['SI'] += 1
            self.registers['DI'] += 1
        else:  # Decrement
            self.registers['SI'] -= 1
            self.registers['DI'] -= 1

    def movsw(self):
        """Move word from source index (SI) to destination index (DI) and update indices."""
        word = (self.memory[self.registers['SI']] << 8) | self.memory[self.registers['SI'] + 1]
        self.memory[self.registers['DI']] = word & 0xFF
        self.memory[self.registers['DI'] + 1] = (word >> 8) & 0xFF
        # Update SI and DI based on the direction flag
        if self.status_flags['DF'] == 0:  # Increment
            self.registers['SI'] += 2
            self.registers['DI'] += 2
        else:  # Decrement
            self.registers['SI'] -= 2
            self.registers['DI'] -= 2

    def cmpsb(self):
        """Compare byte at source index (SI) with destination index (DI)."""
        byte1 = self.memory[self.registers['SI']]
        byte2 = self.memory[self.registers['DI']]
        self.alu('SUB', byte1, byte2)

    def cmpsw(self):
        """Compare word at source index (SI) with destination index (DI)."""
        word1 = (self.memory[self.registers['SI']] << 8) | self.memory[self.registers['SI'] + 1]
        word2 = (self.memory[self.registers['DI']] << 8) | self.memory[self.registers['DI'] + 1]
        self.alu('SUB', word1, word2)

    def stc(self):
        self.status_flags['CF'] = 1

    def clc(self):
        self.status_flags['CF'] = 0

    def print_data_segment(self):
        """打印数据段的内容"""
        print("数据段内容:")
        for label, value in self.data_segment.items():
            print(f"{label}: {value}")

    def print_labels(self):
        """打印标签及其对应的IP位置"""
        print("标签位置:")
        for label, position in self.labels.items():
            print(f"{label}: {position}")

    def print_procedures(self):
        """打印过程定义及其入口点"""
        print("过程定义:")
        for proc, position in self.procedures.items():
            print(f"{proc}: {position}")


class CPU:
    def __init__(self, memory, instructions):
        self.biu = BIU(memory, instructions)  # 将指令列表传递给BIU
        self.eu = EU()
        self.eu.set_memory(memory)
        self.instructions = instructions

    def run(self):
        self.eu.parse_data_segment(self.instructions)  # 解析数据段
        while True:
            if self.eu.registers['IP'] >= len(self.instructions):
                print("IP 寄存器超出指令范围，停止执行")
                break
            instruction = self.biu.fetch_instruction(self.eu.registers['IP'])
            if instruction == 'HLT':  # 如果指令是HLT，则停止执行
                print("停止执行")
                break
            if not self.eu.execute_instruction(instruction):
                break
            self.eu.registers['IP'] += 1  # 成功执行指令后，IP寄存器自增


memory = [0] * 256

# instructions = [
#     "VOICE 01",  # 开启LED
#     "VOICE 03",  # 开启风扇
#     "STATUS LED",  # 查询LED状态
#     "STATUS Fan",  # 查询风扇状态
#     "VOICE 02",  # 关闭LED
#     "VOICE 04",  # 关闭风扇
#     "HLT"        # 停止执行
# ]
#
# memory = [0] * 256
# cpu = CPUWithTimer(memory, instructions)
# cpu.run()


# 示例程序测试定时器功能
# instructions = [
#     "CONFIG_TIMER 1 10",  # 配置模式1，初始值10
#     "START_TIMER",        # 启动定时器
#     "TICK_TIMER",         # 模拟时钟周期
#     "TICK_TIMER",         # 模拟时钟周期
#     "TICK_TIMER",         # 模拟时钟周期
#     "TICK_TIMER",         # 模拟时钟周期
#     "TICK_TIMER",         # 模拟时钟周期
#     "TICK_TIMER",         # 模拟时钟周期
#     "STOP_TIMER",         # 停止定时器
#     "TICK_TIMER",         # 再次模拟时钟周期（不会变化）
#     "HLT"                 # 停止执行
# ]
#
# cpu = CPU(memory, instructions)
# cpu.run()
# cpu.eu.print_data_segment()
# cpu.eu.print_labels()
# cpu.eu.print_procedures()
# print("-----"*20)
#
# instructions = [
#     "WRITE_CTRL 0x80",
#     "WRITE_PORT A 0x0F",
#     "WRITE_PORT B 0x55",
#     "WRITE_PORT C 0x3C",
#     "READ_PORT A",
#     "READ_PORT B",
#     "READ_PORT C",
#     "HLT"
# ]
#
# cpu = CPU(memory, instructions)
# cpu.run()
# cpu.eu.print_data_segment()
# cpu.eu.print_labels()
# cpu.eu.print_procedures()


instructions = [
    # 配置定时器模式1，初始值10，定时器每10个周期触发一次
    "CONFIG_TIMER 1 10",
    # 启动定时器
    "START_TIMER",

    # 模拟定时器周期，定时器会在每次时钟周期触发
    "TICK_TIMER",          # 周期1
    "TICK_TIMER",          # 周期2
    "TICK_TIMER",          # 周期3
    "TICK_TIMER",          # 周期4
    "TICK_TIMER",          # 周期5
    "TICK_TIMER",          # 周期6
    "TICK_TIMER",          # 周期7
    "TICK_TIMER",          # 周期8
    "TICK_TIMER",          # 周期9
    "TICK_TIMER",          # 周期10

    # LED的开关状态
    "VOICE 01",            # 开启LED1
    "TICK_TIMER",          # 周期11
    "VOICE 03",            # 开启LED2
    "TICK_TIMER",          # 周期12
    "VOICE 02",            # 关闭LED1
    "TICK_TIMER",          # 周期13
    "VOICE 04",            # 关闭LED2
    "TICK_TIMER",          # 周期14

    # 风扇的开关状态
    "VOICE 05",            # 开启FAN1
    "TICK_TIMER",          # 周期15
    "VOICE 07",            # 开启FAN2
    "TICK_TIMER",          # 周期16
    "VOICE 06",            # 关闭FAN1
    "TICK_TIMER",          # 周期17
    "VOICE 08",            # 关闭FAN2
    "TICK_TIMER",          # 周期18

    # 停止定时器
    "STOP_TIMER",          # 停止定时器
    "WRITE_CTRL 0x80",
    "WRITE_PORT A 0x0F",
    "WRITE_PORT B 0x55",
    "WRITE_PORT C 0x3C",
    "READ_PORT A",
    "READ_PORT B",
    "READ_PORT C",
    "HLT"                  # 停止执行
]

cpu = CPU(memory, instructions)
cpu.run()
cpu.eu.print_data_segment()
cpu.eu.print_labels()
cpu.eu.print_procedures()
