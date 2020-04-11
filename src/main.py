from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5 import uic

import src.resource_manager as rm  # used to point to resources for pyinstaller
from src import dbg

import sys
import traceback


ui_file = rm.resource_path("ui/main_window.ui")  # <- For every path to resources must
UI_Main_Window, _ = uic.loadUiType(ui_file)


# Defines all the signals to be used for threads
class WorkerSignals(QObject):
    test_func_finished = pyqtSignal()  # This signal will point to a function
    error = pyqtSignal(tuple)


# This worker will be run in a separate thread
class WorkerTest(QRunnable):

    def __init__(self, func, test_string=None):
        super(WorkerTest, self).__init__()
        self.signals = WorkerSignals()  # Provides signals to communicate with main thread
        self.func = func  # This is the function that will be run in this thread
        self.test_string = test_string  # This a parameter passed from the main thread

    @pyqtSlot()
    def run(self) -> None:
        dbg.p("Thread running", "WorkerTest")
        try:
            self.func(self.test_string)  # This runs the function in the worker thread
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.test_func_finished.emit()


# T
class MainWindow(QMainWindow, UI_Main_Window):
    def __init__(self):
        QMainWindow.__init__(self)
        UI_Main_Window.__init__(self)
        self.setupUi(self)
        self.setWindowIcon(QIcon(rm.resource_path('Icon.ico')))

        self.btnTest.clicked.connect(self.btn_test_clicked)

        self.gui_cont = GuiController(self)

    def btn_test_clicked(self):
        dbg.p("Button clicked", "MyWindow")
        new_text = "It works!"
        test_thread = WorkerTest(self.gui_cont.update_label, new_text)
        test_thread.signals.test_func_finished.connect(self.thread_finished)

        test_thread.run()

    def thread_finished(self):
        print("Thread finished!")


class GuiController(QObject):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def update_label(self, new_text):
        self.main_window.lblTest.setText(new_text)
        dbg.p("Label text updated", "GuiController")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    dbg.p("Application started", "main")
    window = MainWindow()
    window.show()
    dbg.p("Window shown", "main")
    exit_code = app.exec_()
    sys.exit(exit_code)
