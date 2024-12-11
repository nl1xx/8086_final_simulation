class Timer8253:
    def __init__(self):
        # 模拟 3 个计数器的控制寄存器和计数寄存器
        self.control_register = 0  # 控制字寄存器
        self.counters = [
            {'counter_register': 0, 'initial_value': 0, 'mode': 0, 'running': False} for _ in range(3)
        ]

    def configure(self, counter, mode, initial_value):
        """配置指定计数器的模式和初始值"""
        if not (0 <= counter <= 2):
            raise ValueError("Invalid counter number. Must be 0, 1, or 2.")

        self.counters[counter]['mode'] = mode
        self.counters[counter]['initial_value'] = initial_value
        self.counters[counter]['counter_register'] = initial_value
        self.counters[counter]['running'] = False  # 配置后默认停止运行

        print(f"Counter {counter} configured: mode={mode}, initial_value={initial_value}")

    def start(self, counter):
        """启动指定的计数器"""
        if not (0 <= counter <= 2):
            raise ValueError("Invalid counter number. Must be 0, 1, or 2.")

        if self.counters[counter]['counter_register'] > 0:
            self.counters[counter]['running'] = True
            print(f"Counter {counter} started")

    def stop(self, counter):
        """停止指定的计数器"""
        if not (0 <= counter <= 2):
            raise ValueError("Invalid counter number. Must be 0, 1, or 2.")

        self.counters[counter]['running'] = False
        print(f"Counter {counter} stopped")

    def tick(self, counter):
        """模拟指定计数器的时钟周期"""
        if not (0 <= counter <= 2):
            raise ValueError("Invalid counter number. Must be 0, 1, or 2.")

        if self.counters[counter]['running'] and self.counters[counter]['counter_register'] > 0:
            self.counters[counter]['counter_register'] -= 1
            print(f"Counter {counter} tick: counter={self.counters[counter]['counter_register']}")

            if self.counters[counter]['counter_register'] == 0:
                self.counters[counter]['running'] = False
                print(f"Counter {counter} reached zero")

    def write_control(self, counter, mode, initial_value):
        """通过控制参数直接配置计数器"""
        if not (0 <= counter <= 2):
            raise ValueError("Invalid counter number. Must be 0, 1, or 2.")

        # 设置控制寄存器的相关位
        self.control_register = (counter << 6) | (mode << 1) | 0x01  # 示例控制字逻辑
        print(f"Control word set: counter={counter}, mode={mode}, initial_value={initial_value}")

        # 调用 configure 方法配置计数器
        self.configure(counter, mode, initial_value)

    def read_counter(self, counter):
        """读取指定计数器的当前值"""
        if not (0 <= counter <= 2):
            raise ValueError("Invalid counter number. Must be 0, 1, or 2.")

        value = self.counters[counter]['counter_register']
        print(f"Counter {counter} read: {value}")
        return value

    def write_counter(self, counter, value):
        """向指定计数器写入初始值"""
        if not (0 <= counter <= 2):
            raise ValueError("Invalid counter number. Must be 0, 1, or 2.")

        self.counters[counter]['initial_value'] = value
        self.counters[counter]['counter_register'] = value
        print(f"Counter {counter} written: initial_value={value}")

# # 示例用法
# timer = Timer8253()
#
# # 配置计数器 0 为模式 2，初始值 10
# timer.configure(counter=0, mode=2, initial_value=10)
#
# # 启动计数器 0
# timer.start(counter=0)
#
# # 模拟计数器 0 的时钟周期
# timer.tick(counter=0)
# timer.tick(counter=0)
# timer.tick(counter=0)
#
# # 停止计数器 0
# timer.stop(counter=0)
#
# # 读取计数器 0 的当前值
# timer.read_counter(counter=0)
#
# # 写入计数器 1 的初始值
# timer.write_counter(counter=1, value=20)
#
# # 写入控制字
# timer.write_control(control_word=0b10101010)

