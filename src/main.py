import sys
from PyQt5.QtWidgets import QApplication
from controllers.timer_controller import TimerController

def main():
    app = QApplication(sys.argv)
    controller = TimerController()
    controller.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main() 