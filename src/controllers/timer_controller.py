from PyQt5.QtCore import QTimer
from models.timer_model import TimerModel
from views.main_window import MainWindow

class TimerController:
    def __init__(self):
        self.model = TimerModel()
        self.view = MainWindow(self)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        
        # 加载数据并更新UI
        self.model.load_data()
        self.update_ui()
    
    def update_ui(self):
        """更新所有UI元素"""
        # 更新设置
        settings = {
            'work_duration': self.model.work_duration,
            'short_break_duration': self.model.short_break_duration,
            'long_break_duration': self.model.long_break_duration,
            'long_break_interval': self.model.long_break_interval
        }
        self.view.update_settings(settings)
        
        # 更新统计信息
        stats = {
            'date': self.model.current_date,
            'completed_tomatoes': self.model.current_cycle,
            'internal_interruptions': self.model.internal_interruptions,
            'external_interruptions': self.model.external_interruptions
        }
        self.view.update_stats(stats)
        
        # 更新任务列表
        self.view.update_tasks_list(self.model.daily_tasks, self.model.completed_tasks)
        
        # 更新计时器显示
        self.view.update_timer_display(self.format_time(self.model.remaining_seconds))
    
    def format_time(self, seconds):
        """将秒数格式化为MM:SS"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def start_timer(self):
        """开始计时器"""
        if not self.model.is_working and not self.model.is_paused:
            # 新开始一个番茄
            task_input = self.view.get_task_input()
            self.model.current_task = task_input['name']
            self.model.tomatoes_planned = task_input['tomatoes']
            self.model.is_working = True
            self.model.remaining_seconds = self.model.work_duration * 60
            
            # 更新UI
            self.view.update_status("工作中")
            self.view.set_button_states(False, True)
            self.view.set_timer_color("#d32f2f")  # 红色
            
            # 如果任务内容不为空，添加到今日任务
            if self.model.current_task:
                self.add_task()
        elif self.model.is_paused:
            # 从暂停状态恢复
            self.model.is_paused = False
            self.view.update_status("工作中" if self.model.is_working else "休息中")
            self.view.set_button_states(False, True)
        
        self.timer.start(1000)  # 每秒更新一次
    
    def pause_timer(self):
        """暂停计时器"""
        self.model.is_paused = True
        self.timer.stop()
        self.view.update_status("已暂停")
        self.view.set_button_states(True, False)
    
    def reset_timer(self):
        """重置计时器"""
        self.timer.stop()
        self.model.is_working = False
        self.model.is_paused = False
        self.model.remaining_seconds = self.model.work_duration * 60
        
        # 更新UI
        self.view.update_timer_display(self.format_time(self.model.remaining_seconds))
        self.view.update_status("准备开始")
        self.view.set_button_states(True, False)
        self.view.set_timer_color("#333333")  # 默认颜色
    
    def update_timer(self):
        """更新计时器显示"""
        self.model.check_date_change()
        
        if self.model.remaining_seconds > 0:
            self.model.remaining_seconds -= 1
            self.view.update_timer_display(self.format_time(self.model.remaining_seconds))
        else:
            self.timer.stop()
            if self.model.is_working:
                # 工作时间结束，开始休息
                self.model.is_working = False
                self.model.current_cycle += 1
                
                # 检查是否需要长休息
                if self.model.current_cycle % self.model.long_break_interval == 0:
                    self.model.remaining_seconds = self.model.long_break_duration * 60
                    self.view.update_status("长休息中")
                else:
                    self.model.remaining_seconds = self.model.short_break_duration * 60
                    self.view.update_status("短休息中")
                
                # 更新UI颜色为休息状态
                self.view.set_timer_color("#388e3c")  # 绿色
                
                # 标记任务完成
                self.model.mark_task_completed()
                self.update_ui()
            else:
                # 休息时间结束，开始工作
                self.model.is_working = True
                self.model.remaining_seconds = self.model.work_duration * 60
                self.view.update_status("工作中")
                
                # 更新UI颜色为工作状态
                self.view.set_timer_color("#d32f2f")  # 红色
            
            self.timer.start(1000)
    
    def add_task(self):
        """添加任务"""
        task_input = self.view.get_task_input()
        if self.model.add_task(task_input['name'], task_input['tomatoes']):
            self.view.clear_task_input()
            self.update_ui()
        else:
            self.view.show_message("错误", "请输入任务内容！")
    
    def save_settings(self):
        """保存设置"""
        settings = self.view.get_settings()
        
        # 计算时间变化比例（用于正在运行的计时器）
        time_ratio = 1
        if self.model.is_working and self.model.work_duration > 0:
            time_ratio = settings['work_duration'] / self.model.work_duration
        
        # 更新设置
        self.model.work_duration = settings['work_duration']
        self.model.short_break_duration = settings['short_break_duration']
        self.model.long_break_duration = settings['long_break_duration']
        self.model.long_break_interval = settings['long_break_interval']
        
        # 更新计时器显示
        if self.model.is_working:
            # 如果是工作时间，按比例调整剩余时间
            self.model.remaining_seconds = int(self.model.remaining_seconds * time_ratio)
        elif not self.model.is_paused:
            # 如果未开始，重置为新的工作时间
            self.model.remaining_seconds = self.model.work_duration * 60
        
        # 更新显示
        self.view.update_timer_display(self.format_time(self.model.remaining_seconds))
        
        # 保存设置
        self.model.save_data()
        self.view.show_message("设置已保存", "计时器设置已成功更新！")
    
    def record_internal_interruption(self):
        """记录内部打断"""
        self.model.internal_interruptions += 1
        self.model.save_data()
        self.update_ui()
        self.view.show_message("打断记录", "已记录一次内部打断")
    
    def record_external_interruption(self):
        """记录外部打断"""
        self.model.external_interruptions += 1
        self.model.save_data()
        self.update_ui()
        self.view.show_message("打断记录", "已记录一次外部打断")
    
    def show(self):
        """显示主窗口"""
        self.view.show() 
