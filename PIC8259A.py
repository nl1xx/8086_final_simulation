class PIC8259A:
    def __init__(self):
        self.IRR = 0b00000000  # 中断请求寄存器
        self.ISR = 0b00000000  # 中断服务寄存器
        self.IMR = 0b00000000  # 中断屏蔽寄存器
        self.priority = [i for i in range(8)]  # 中断优先级
        self.nested_interrupts = 0  # 嵌套中断计数

        # 模拟 INTA 引脚，默认情况下为低电平（0）
        self.INTA = 0  # 0 表示低电平（没有响应），1 表示高电平（响应中断请求）


    def set_INTA(self, value):
        """设置 INTA 信号"""
        if value not in [0, 1]:
            raise ValueError("INTA 信号只接受 0 或 1")
        self.INTA = value

    def get_INTA(self):
        """获取 INTA 信号的当前状态"""
        return self.INTA

    def handle_interrupt(self):
        """模拟处理中断的过程"""
        # 处理中断时，需要触发 INTA 信号，通常会设置为高电平（1）
        self.set_INTA(1)  # 激活 INTA 信号
        self.current_interrupt = self._get_next_interrupt()

        # 假设处理完中断后，INTA 信号变为低电平（0）
        self.set_INTA(0)

    def request_interrupt(self, irq):
        if irq < 0 or irq > 7:
            raise ValueError("无效的 IRQ 号 (0-7)")
        self.IRR |= (1 << irq)
        print(f"中断请求 IRQ{irq} 发出")

    def mask_interrupt(self, irq):
        self.IMR |= (1 << irq)  # 数字1左移irq位, 在IRR中设置正确的位
        print(f"IRQ{irq} 被屏蔽")

    def unmask_interrupt(self, irq):
        self.IMR &= ~(1 << irq)
        print(f"IRQ{irq} 被取消屏蔽")

    def check_interrupt(self):
        for irq in self.priority:
            if (self.IRR & (1 << irq)) != 0 and (self.IMR & (1 << irq)) == 0:
                return irq
        return -1

    def acknowledge_interrupt(self, irq):
        self.IRR &= ~(1 << irq)
        self.ISR |= (1 << irq)
        self.nested_interrupts += 1
        print(f"中断 IRQ{irq} 被确认并处理")

    def end_of_interrupt(self, irq):
        self.ISR &= ~(1 << irq)
        self.nested_interrupts -= 1
        print(f"中断 IRQ{irq} 处理结束")

    def rotate_priority(self):
        self.priority = self.priority[1:] + self.priority[:1]
        print(f"中断优先级轮转: {self.priority}")
