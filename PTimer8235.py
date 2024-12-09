class Timer8235:
    def __init__(self):
        # 模拟定时器的控制寄存器和计数寄存器
        self.control_register = 0  # 模式选择和控制
        self.counter_register = 0  # 当前计数值
        self.mode = 0  # 定时器工作模式
        self.running = False  # 定时器状态

    def configure(self, mode, initial_value):
        """配置定时器的模式和初始值"""
        self.mode = mode
        self.counter_register = initial_value
        self.running = False  # 配置后默认停止运行
        print(f"Timer configured: mode={mode}, initial_value={initial_value}")

    def start(self):
        """启动定时器"""
        if self.counter_register > 0:
            self.running = True
            print("Timer started")

    def stop(self):
        """停止定时器"""
        self.running = False
        print("Timer stopped")

    def tick(self):
        """模拟时钟周期"""
        if self.running and self.counter_register > 0:
            self.counter_register -= 1
            print(f"Timer tick: counter={self.counter_register}")
            if self.counter_register == 0:
                self.running = False
                print("Timer reached zero")
