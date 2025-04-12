from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QSpinBox, QLineEdit, 
                             QListWidget, QTabWidget, QFormLayout, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("番茄工作法计时器")
        self.setGeometry(100, 100, 800, 600)
        
        # 初始化UI
        self.init_ui()
        self.set_style()
        
    def init_ui(self):
        # 主窗口布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # 左侧面板（计时器和任务输入）
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # 计时器显示
        self.timer_display = QLabel("25:00")
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
        self.start_button.clicked.connect(self.controller.start_timer)
        control_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("暂停")
        self.pause_button.clicked.connect(self.controller.pause_timer)
        self.pause_button.setEnabled(False)
        control_layout.addWidget(self.pause_button)
        
        self.reset_button = QPushButton("重置")
        self.reset_button.clicked.connect(self.controller.reset_timer)
        control_layout.addWidget(self.reset_button)
        
        left_layout.addWidget(control_group)
        
        # 打断按钮
        interrupt_group = QGroupBox("打断记录")
        interrupt_layout = QHBoxLayout(interrupt_group)
        
        self.internal_button = QPushButton("内部打断 (+1)")
        self.internal_button.clicked.connect(self.controller.record_internal_interruption)
        interrupt_layout.addWidget(self.internal_button)
        
        self.external_button = QPushButton("外部打断 (+1)")
        self.external_button.clicked.connect(self.controller.record_external_interruption)
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
        self.add_task_button.clicked.connect(self.controller.add_task)
        task_layout.addRow(self.add_task_button)
        
        left_layout.addWidget(task_group)
        
        # 右侧面板（设置和记录）
        right_panel = QTabWidget()
        
        # 设置标签页
        settings_tab = QWidget()
        settings_layout = QFormLayout(settings_tab)
        
        self.work_time_input = QSpinBox()
        self.work_time_input.setMinimum(1)
        self.work_time_input.setValue(25)
        settings_layout.addRow("工作时间 (分钟):", self.work_time_input)
        
        self.short_break_input = QSpinBox()
        self.short_break_input.setMinimum(1)
        self.short_break_input.setValue(5)
        settings_layout.addRow("短休息时间 (分钟):", self.short_break_input)
        
        self.long_break_input = QSpinBox()
        self.long_break_input.setMinimum(1)
        self.long_break_input.setValue(15)
        settings_layout.addRow("长休息时间 (分钟):", self.long_break_input)
        
        self.long_break_interval_input = QSpinBox()
        self.long_break_interval_input.setMinimum(1)
        self.long_break_interval_input.setValue(4)
        settings_layout.addRow("长休息间隔 (番茄数):", self.long_break_interval_input)
        
        save_settings_button = QPushButton("保存设置")
        save_settings_button.clicked.connect(self.controller.save_settings)
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
        
        self.today_label = QLabel("日期: ")
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
            QSpinBox, QLineEdit {
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
    
    def update_timer_display(self, time_str):
        self.timer_display.setText(time_str)
    
    def update_status(self, status):
        self.status_label.setText(status)
    
    def update_stats(self, stats):
        self.today_label.setText(f"日期: {stats['date']}")
        self.completed_tomatoes_label.setText(f"已完成番茄: {stats['completed_tomatoes']}")
        self.internal_interruptions_label.setText(f"内部打断: {stats['internal_interruptions']}")
        self.external_interruptions_label.setText(f"外部打断: {stats['external_interruptions']}")
    
    def update_tasks_list(self, daily_tasks, completed_tasks):
        self.tasks_list.clear()
        for task in daily_tasks:
            item_text = f"{task['name']} (计划: {task['planned']}番茄, 已完成: {task['completed']})"
            self.tasks_list.addItem(item_text)
        
        self.completed_list.clear()
        for task in completed_tasks:
            item_text = f"{task['name']} (完成: {task['completed']}/{task['planned']}番茄)"
            self.completed_list.addItem(item_text)
    
    def update_settings(self, settings):
        self.work_time_input.setValue(settings['work_duration'])
        self.short_break_input.setValue(settings['short_break_duration'])
        self.long_break_input.setValue(settings['long_break_duration'])
        self.long_break_interval_input.setValue(settings['long_break_interval'])
    
    def get_settings(self):
        return {
            'work_duration': self.work_time_input.value(),
            'short_break_duration': self.short_break_input.value(),
            'long_break_duration': self.long_break_input.value(),
            'long_break_interval': self.long_break_interval_input.value()
        }
    
    def get_task_input(self):
        return {
            'name': self.task_input.text(),
            'tomatoes': self.tomatoes_input.value()
        }
    
    def clear_task_input(self):
        self.task_input.clear()
        self.tomatoes_input.setValue(1)
    
    def set_timer_color(self, color):
        palette = self.timer_display.palette()
        palette.setColor(QPalette.WindowText, QColor(color))
        self.timer_display.setPalette(palette)
    
    def set_button_states(self, start_enabled, pause_enabled):
        self.start_button.setEnabled(start_enabled)
        self.pause_button.setEnabled(pause_enabled)
    
    def show_message(self, title, message):
        QMessageBox.information(self, title, message) 