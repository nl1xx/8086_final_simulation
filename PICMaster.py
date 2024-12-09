from PIC8259A import PIC8259A

class PICMaster(PIC8259A):
    def __init__(self, slave_pic):
        super().__init__()
        self.slave_pic = slave_pic  # 从控制器
        self.irq2 = 0  # 使用IR2引脚 (与从8259A连接)

    def request_interrupt(self, irq_num):
        """主控制器触发中断，检查是否是级联中断"""
        if irq_num == 2:
            self.irq2 = 1  # IR2 被触发，表示需要访问从控制器
            print("PICMaster: IR2 被触发，访问从控制器。")
        else:
            # 调用父类的中断确认方法
            super().acknowledge_interrupt(irq_num)

    def service_interrupt(self,slave_irq):
        """主控制器服务中断，检查级联请求"""
        if self.irq2 == 1:
            self.irq2 = 0  # 重置 IR2
            print("PICMaster: 处理中断请求，访问从控制器。")
            # 访问从控制器并响应中断
            self.slave_pic.acknowledge_interrupt(slave_irq)
        else:
            # 处理当前主控制器的中断
            return super().acknowledge_interrupt(slave_irq)



