import sys, os
import time, json
from datetime import datetime, date
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QSpinBox, QLineEdit, QTextEdit, 
                             QListWidget, QTabWidget, QFormLayout, QMessageBox, QGroupBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QPalette, QColor

class TomatoTimer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("番茄工作法计时器")
        self.setGeometry(100, 100, 800, 600)
        
        # 初始化变量
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
        self.today = date.today().strftime("%Y-%m-%d")
        self.daily_tasks = []  # 今日任务列表
        self.completed_tasks = []  # 已完成任务列表
        
        # 初始化UI
        self.init_ui()
        
        # 初始化计时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.data_file = "tomato_timer_data.json"
        
        # 加载保存的数据
        self.load_data()

    def load_data(self):
        """从文件加载保存的数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    
                    # 加载设置
                    settings = data.get('settings', {})
                    self.work_duration = settings.get('work_duration', 25)
                    self.short_break_duration = settings.get('short_break_duration', 5)
                    self.long_break_duration = settings.get('long_break_duration', 15)
                    self.long_break_interval = settings.get('long_break_interval', 4)
                    
                    # 更新UI中的设置值
                    self.work_time_input.setValue(self.work_duration)
                    self.short_break_input.setValue(self.short_break_duration)
                    self.long_break_input.setValue(self.long_break_duration)
                    self.long_break_interval_input.setValue(self.long_break_interval)
                    
                    # 加载后立即更新计时器显示
                    self.remaining_seconds = self.work_duration * 60  # 初始化为工作时间
                    self.timer_display.setText(self.format_time(self.remaining_seconds))
                    
                    # 加载统计数据和任务
                    stats = data.get('stats', {})
                    self.current_cycle = stats.get('completed_tomatoes', 0)
                    self.internal_interruptions = stats.get('internal_interruptions', 0)
                    self.external_interruptions = stats.get('external_interruptions', 0)
                    
                    # 加载任务列表
                    self.daily_tasks = data.get('daily_tasks', [])
                    self.completed_tasks = data.get('completed_tasks', [])
                    
                    # 更新UI
                    self.update_stats()
                    self.update_tasks_list()
                    
            except Exception as e:
                QMessageBox.warning(self, "加载错误", f"无法加载保存的数据: {str(e)}")
                # 加载失败时使用默认值初始化计时器
                self.remaining_seconds = self.work_duration * 60
                self.timer_display.setText(self.format_time(self.remaining_seconds))
        else:
            # 新文件时使用默认值初始化计时器
            self.remaining_seconds = self.work_duration * 60
            self.timer_display.setText(self.format_time(self.remaining_seconds))
    
    def reset_daily_data(self):
        """重置每日数据（保留设置）"""
        self.current_cycle = 0
        self.internal_interruptions = 0
        self.external_interruptions = 0
        self.daily_tasks = []
        self.completed_tasks = []
        
        # 更新UI
        self.update_stats()
        self.update_tasks_list()
        
        # 保存初始数据
        self.save_data()
    
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
                'internal_interruptions': sum(t['internal_interruptions'] for t in self.completed_tasks) + self.internal_interruptions,
                'external_interruptions': sum(t['external_interruptions'] for t in self.completed_tasks) + self.external_interruptions
            },
            'daily_tasks': self.daily_tasks,
            'completed_tasks': self.completed_tasks
        }
        
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "保存错误", f"无法保存数据: {str(e)}")
    
    def check_date_change(self):
        """检查日期变化，如果是新的一天则重置每日数据"""
        today = date.today().strftime("%Y-%m-%d")
        if today != self.current_date:
            self.current_date = today
            self.data_file = os.path.join(self.data_dir, f"{self.current_date}.json")
            self.reset_daily_data()
    
    def closeEvent(self, event):
        """窗口关闭时保存数据"""
        self.save_data()
        event.accept()
    
    def save_settings(self):
        """保存设置"""
        # 获取新设置值
        new_work_duration = self.work_time_input.value()
        new_short_break = self.short_break_input.value()
        new_long_break = self.long_break_input.value()
        new_interval = self.long_break_interval_input.value()
        
        # 计算时间变化比例（用于正在运行的计时器）
        time_ratio = 1
        if self.is_working and self.work_duration > 0:
            time_ratio = new_work_duration / self.work_duration
        
        # 更新设置
        self.work_duration = new_work_duration
        self.short_break_duration = new_short_break
        self.long_break_duration = new_long_break
        self.long_break_interval = new_interval
        
        # 更新计时器显示
        if self.is_working:
            # 如果是工作时间，按比例调整剩余时间
            self.remaining_seconds = int(self.remaining_seconds * time_ratio)
        elif self.is_paused:
            # 如果暂停状态，保持当前显示不变
            pass
        else:
            # 如果未开始，重置为新的工作时间
            self.remaining_seconds = self.work_duration * 60
        
        # 更新显示
        self.timer_display.setText(self.format_time(self.remaining_seconds))
        
        # 保存设置
        self.save_data()
        QMessageBox.information(self, "设置已保存", "计时器设置已成功更新！")
        
    def init_ui(self):
        # 主窗口布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # 左侧面板（计时器和任务输入）
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 计时器显示
        self.timer_display = QLabel(self.format_time(self.remaining_seconds))
        self.timer_display.setAlignment(Qt.AlignCenter)
        self.timer_display.setFont(QFont("Arial", 48, QFont.Bold))
        left_layout.addWidget(self.timer_display)
        
        # 状态显示
        self.status_label = QLabel("准备开始")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 16))
        left_layout.addWidget(self.status_label)
        
        # 控制按钮
        control_group = QGroupBox("控制")
        control_layout = QHBoxLayout(control_group)
        
        self.start_button = QPushButton("开始")
        self.start_button.clicked.connect(self.start_timer)
        control_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("暂停")
        self.pause_button.clicked.connect(self.pause_timer)
        self.pause_button.setEnabled(False)
        control_layout.addWidget(self.pause_button)
        
        self.reset_button = QPushButton("重置")
        self.reset_button.clicked.connect(self.reset_timer)
        control_layout.addWidget(self.reset_button)
        
        left_layout.addWidget(control_group)
        
        # 打断按钮
        interrupt_group = QGroupBox("打断记录")
        interrupt_layout = QHBoxLayout(interrupt_group)
        
        self.internal_button = QPushButton("内部打断 (+1)")
        self.internal_button.clicked.connect(self.record_internal_interruption)
        interrupt_layout.addWidget(self.internal_button)
        
        self.external_button = QPushButton("外部打断 (+1)")
        self.external_button.clicked.connect(self.record_external_interruption)
        interrupt_layout.addWidget(self.external_button)
        
        left_layout.addWidget(interrupt_group)
        
        # 任务输入
        task_group = QGroupBox("任务设置")
        task_layout = QFormLayout(task_group)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("输入任务内容")
        task_layout.addRow("任务内容:", self.task_input)
        
        self.tomatoes_input = QSpinBox()
        self.tomatoes_input.setMinimum(1)
        self.tomatoes_input.setValue(1)
        task_layout.addRow("计划番茄数:", self.tomatoes_input)
        
        self.add_task_button = QPushButton("添加任务")
        self.add_task_button.clicked.connect(self.add_task)
        task_layout.addRow(self.add_task_button)
        
        left_layout.addWidget(task_group)
        
        # 右侧面板（设置和记录）
        right_panel = QTabWidget()
        
        # 设置标签页
        settings_tab = QWidget()
        settings_layout = QFormLayout(settings_tab)
        
        self.work_time_input = QSpinBox()
        self.work_time_input.setMinimum(1)
        self.work_time_input.setValue(self.work_duration)
        settings_layout.addRow("工作时间 (分钟):", self.work_time_input)
        
        self.short_break_input = QSpinBox()
        self.short_break_input.setMinimum(1)
        self.short_break_input.setValue(self.short_break_duration)
        settings_layout.addRow("短休息时间 (分钟):", self.short_break_input)
        
        self.long_break_input = QSpinBox()
        self.long_break_input.setMinimum(1)
        self.long_break_input.setValue(self.long_break_duration)
        settings_layout.addRow("长休息时间 (分钟):", self.long_break_input)
        
        self.long_break_interval_input = QSpinBox()
        self.long_break_interval_input.setMinimum(1)
        self.long_break_interval_input.setValue(self.long_break_interval)
        settings_layout.addRow("长休息间隔 (番茄数):", self.long_break_interval_input)
        
        save_settings_button = QPushButton("保存设置")
        save_settings_button.clicked.connect(self.save_settings)
        settings_layout.addRow(save_settings_button)
        
        right_panel.addTab(settings_tab, "设置")
        
        # 今日任务标签页
        tasks_tab = QWidget()
        tasks_layout = QVBoxLayout(tasks_tab)
        
        self.tasks_list = QListWidget()
        tasks_layout.addWidget(QLabel("今日任务:"))
        tasks_layout.addWidget(self.tasks_list)
        
        self.completed_list = QListWidget()
        tasks_layout.addWidget(QLabel("已完成任务:"))
        tasks_layout.addWidget(self.completed_list)
        
        right_panel.addTab(tasks_tab, "任务记录")
        
        # 统计标签页
        stats_tab = QWidget()
        stats_layout = QFormLayout(stats_tab)
        
        self.today_label = QLabel(f"日期: {self.today}")
        stats_layout.addRow(self.today_label)
        
        self.completed_tomatoes_label = QLabel("已完成番茄: 0")
        stats_layout.addRow(self.completed_tomatoes_label)
        
        self.internal_interruptions_label = QLabel("内部打断: 0")
        stats_layout.addRow(self.internal_interruptions_label)
        
        self.external_interruptions_label = QLabel("外部打断: 0")
        stats_layout.addRow(self.external_interruptions_label)
        
        right_panel.addTab(stats_tab, "统计")
        
        # 将左右面板添加到主布局
        main_layout.addWidget(left_panel, 2)
        main_layout.addWidget(right_panel, 1)
        
        # 设置样式
        self.set_style()
    
    def set_style(self):
        # 设置应用样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 8px 16px;
                text-align: center;
                text-decoration: none;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3e8e41;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 3px;
                background-color: white;
            }
            QSpinBox, QLineEdit, QTextEdit {
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
            }
            QTabBar::tab {
                padding: 8px;
                background: #e0e0e0;
                border: 1px solid #ddd;
                border-bottom: none;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QTabBar::tab:selected {
                background: #f5f5f5;
                border-bottom: 1px solid #f5f5f5;
                margin-bottom: -1px;
            }
        """)
        
        # 设置计时器颜色
        palette = self.timer_display.palette()
        palette.setColor(QPalette.WindowText, QColor("#333333"))
        self.timer_display.setPalette(palette)
        
        # 设置状态标签颜色
        palette = self.status_label.palette()
        palette.setColor(QPalette.WindowText, QColor("#555555"))
        self.status_label.setPalette(palette)
    
    def format_time(self, seconds):
        """将秒数格式化为MM:SS"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def start_timer(self):
        """开始计时器"""
        if not self.is_working and not self.is_paused:
            # 新开始一个番茄
            self.current_task = self.task_input.text()
            self.tomatoes_planned = self.tomatoes_input.value()
            self.is_working = True
            self.remaining_seconds = self.work_duration * 60
            self.status_label.setText("工作中")
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            
            # 更新UI颜色为工作状态
            palette = self.timer_display.palette()
            palette.setColor(QPalette.WindowText, QColor("#d32f2f"))  # 红色
            self.timer_display.setPalette(palette)
            
            # 如果任务内容不为空，添加到今日任务
            if self.current_task and self.current_task not in [task['name'] for task in self.daily_tasks]:
                self.add_task()
        elif self.is_paused:
            # 从暂停状态恢复
            self.is_paused = False
            self.status_label.setText("工作中" if self.is_working else "休息中")
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
        
        self.timer.start(1000)  # 每秒更新一次
    
    def pause_timer(self):
        """暂停计时器"""
        self.is_paused = True
        self.timer.stop()
        self.status_label.setText("已暂停")
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
    
    def reset_timer(self):
        """重置计时器"""
        self.timer.stop()
        self.is_working = False
        self.is_paused = False
        self.remaining_seconds = self.work_duration * 60  # 使用当前设置的工作时间
        self.timer_display.setText(self.format_time(self.remaining_seconds))
        self.status_label.setText("准备开始")
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        
        # 重置UI颜色
        palette = self.timer_display.palette()
        palette.setColor(QPalette.WindowText, QColor("#333333"))
        self.timer_display.setPalette(palette)
    
    def update_timer(self):
        self.check_date_change()
        """更新计时器显示"""
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.timer_display.setText(self.format_time(self.remaining_seconds))
        else:
            self.timer.stop()
            if self.is_working:
                # 工作时间结束，开始休息
                self.is_working = False
                self.current_cycle += 1
                self.completed_tomatoes_label.setText(f"已完成番茄: {self.current_cycle}")
                
                # 检查是否需要长休息
                if self.current_cycle % self.long_break_interval == 0:
                    self.remaining_seconds = self.long_break_duration * 60
                    self.status_label.setText("长休息中")
                else:
                    self.remaining_seconds = self.short_break_duration * 60
                    self.status_label.setText("短休息中")
                
                # 更新UI颜色为休息状态
                palette = self.timer_display.palette()
                palette.setColor(QPalette.WindowText, QColor("#388e3c"))  # 绿色
                self.timer_display.setPalette(palette)
                
                # 标记任务完成
                self.mark_task_completed()
            else:
                # 休息时间结束，开始工作
                self.is_working = True
                self.remaining_seconds = self.work_duration * 60
                self.status_label.setText("工作中")
                
                # 更新UI颜色为工作状态
                palette = self.timer_display.palette()
                palette.setColor(QPalette.WindowText, QColor("#d32f2f"))  # 红色
                self.timer_display.setPalette(palette)
            
            self.timer.start(1000)
    
    def add_task(self):
        """添加任务到今日任务列表"""
        task_name = self.task_input.text()
        tomatoes = self.tomatoes_input.value()
        
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
            
            self.update_tasks_list()
            self.task_input.clear()
            self.tomatoes_input.setValue(1)
            self.save_data()  # 保存任务
        else:
            QMessageBox.warning(self, "错误", "请输入任务内容！")
    
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
            self.update_tasks_list()
            self.update_stats()
            self.save_data()  # 保存任务状态
    
    def update_tasks_list(self):
        """更新任务列表显示"""
        self.tasks_list.clear()
        for task in self.daily_tasks:
            item_text = f"{task['name']} (计划: {task['planned']}番茄, 已完成: {task['completed']})"
            self.tasks_list.addItem(item_text)
        
        self.completed_list.clear()
        for task in self.completed_tasks:
            item_text = f"{task['name']} (完成: {task['completed']}/{task['planned']}番茄)"
            self.completed_list.addItem(item_text)
    
    def update_stats(self):
        """更新统计信息"""
        total_internal = sum(t['internal_interruptions'] for t in self.completed_tasks) + self.internal_interruptions
        total_external = sum(t['external_interruptions'] for t in self.completed_tasks) + self.external_interruptions
        
        self.internal_interruptions_label.setText(f"内部打断: {total_internal}")
        self.external_interruptions_label.setText(f"外部打断: {total_external}")
    
    def record_internal_interruption(self):
        """记录内部打断"""
        self.internal_interruptions += 1
        self.update_stats()
        self.save_data()
        QMessageBox.information(self, "打断记录", "已记录一次内部打断")
    
    def record_external_interruption(self):
        """记录外部打断"""
        self.external_interruptions += 1
        self.update_stats()
        self.save_data()
        QMessageBox.information(self, "打断记录", "已记录一次外部打断")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    timer = TomatoTimer()
    timer.show()
    sys.exit(app.exec_())