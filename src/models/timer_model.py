from datetime import date
import json
import os

class TimerModel:
    def __init__(self):
        self.work_duration = 25  # 默认工作时间（分钟）
        self.short_break_duration = 5  # 默认短休息时间（分钟）
        self.long_break_duration = 15  # 默认长休息时间（分钟）
        self.long_break_interval = 4  # 长休息间隔（几个番茄后）
        self.current_cycle = 0  # 当前完成的番茄数
        self.is_working = False  # 是否在工作状态
        self.is_paused = False  # 是否暂停
        self.remaining_seconds = self.work_duration * 60  # 剩余秒数
        self.current_task = ""  # 当前任务
        self.tomatoes_planned = 1  # 计划番茄数
        self.internal_interruptions = 0  # 内部打断次数
        self.external_interruptions = 0  # 外部打断次数
        
        # 每日任务记录
        self.current_date = date.today().strftime("%Y-%m-%d")
        self.daily_tasks = []  # 今日任务列表
        self.completed_tasks = []  # 已完成任务列表
        self.data_file = "tomato_timer_data.json"

    def load_data(self):
        """从文件加载保存的数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    
                    # 加载设置
                    settings = data.get('settings', {})
                    self.work_duration = settings.get('work_duration', 25)
                    self.remaining_seconds = self.work_duration * 60 
                    self.short_break_duration = settings.get('short_break_duration', 5)
                    self.long_break_duration = settings.get('long_break_duration', 15)
                    self.long_break_interval = settings.get('long_break_interval', 4)
                    
                    # 加载统计数据和任务
                    stats = data.get('stats', {})
                    self.current_cycle = stats.get('completed_tomatoes', 0)
                    self.internal_interruptions = stats.get('internal_interruptions', 0)
                    self.external_interruptions = stats.get('external_interruptions', 0)
                    
                    # 加载任务列表
                    self.daily_tasks = data.get('daily_tasks', [])
                    self.completed_tasks = data.get('completed_tasks', [])
                    
            except Exception as e:
                print(f"加载数据错误: {str(e)}")
                self.reset_daily_data()

    def save_data(self):
        """保存数据到文件"""
        data = {
            'date': self.current_date,
            'settings': {
                'work_duration': self.work_duration,
                'short_break_duration': self.short_break_duration,
                'long_break_duration': self.long_break_duration,
                'long_break_interval': self.long_break_interval
            },
            'stats': {
                'completed_tomatoes': self.current_cycle,
                'internal_interruptions': self.internal_interruptions,
                'external_interruptions': self.external_interruptions
            },
            'daily_tasks': self.daily_tasks,
            'completed_tasks': self.completed_tasks
        }
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"保存数据错误: {str(e)}")

    def reset_daily_data(self):
        """重置每日数据（保留设置）"""
        self.current_cycle = 0
        self.internal_interruptions = 0
        self.external_interruptions = 0
        self.daily_tasks = []
        self.completed_tasks = []
        self.save_data()

    def check_date_change(self):
        """检查日期变化，如果是新的一天则重置每日数据"""
        today = date.today().strftime("%Y-%m-%d")
        if today != self.current_date:
            self.current_date = today
            self.reset_daily_data()

    def add_task(self, task_name, tomatoes):
        """添加任务到今日任务列表"""
        if task_name:
            task = {
                'name': task_name,
                'planned': tomatoes,
                'completed': 0,
                'internal_interruptions': 0,
                'external_interruptions': 0
            }
            
            # 检查是否已存在相同任务
            existing_task = next((t for t in self.daily_tasks if t['name'] == task_name), None)
            if existing_task:
                existing_task['planned'] += tomatoes
            else:
                self.daily_tasks.append(task)
            
            self.save_data()
            return True
        return False

    def mark_task_completed(self):
        """标记当前任务完成一个番茄"""
        if self.current_task:
            for task in self.daily_tasks:
                if task['name'] == self.current_task:
                    task['completed'] += 1
                    task['internal_interruptions'] += self.internal_interruptions
                    task['external_interruptions'] += self.external_interruptions
                    
                    # 如果完成数达到计划数，移动到已完成列表
                    if task['completed'] >= task['planned']:
                        self.daily_tasks.remove(task)
                        self.completed_tasks.append(task)
                    
                    break
            
            self.internal_interruptions = 0
            self.external_interruptions = 0
            self.save_data()
            return True
        return False 
