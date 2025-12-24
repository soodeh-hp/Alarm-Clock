from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QLabel, QPushButton, QStackedWidget,
    QSpinBox, QTimeEdit, QMessageBox
)
from PyQt5.QtMultimedia import QSound
from PyQt5 import uic
from PyQt5.QtCore import QTimer, QTime
from datetime import datetime
import sys




class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        # Load UI file
        uic.loadUi('alarmclock.ui', self)


        # define main window widgets
        self.background_label = self.findChild(QLabel, "background_label")
        self.bar_label = self.findChild(QLabel, "bar_label")
        self.date_label = self.findChild(QLabel, "date_label")
        self.time_label = self.findChild(QLabel, "time_label")
        self.alarm_pushButton = self.findChild(QPushButton, "alarm_pushButton")
        self.timer_pushButton = self.findChild(QPushButton, "timer_pushButton")
        self.stopwatch_pushButton = self.findChild(QPushButton, "stopwatch_pushButton")
        self.stackedWidget = self.findChild(QStackedWidget, "stackedWidget")


        # Navigation between pages
        self.alarm_pushButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.timer_pushButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.stopwatch_pushButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.stackedWidget.setCurrentIndex(0)



        #___________________________ Alarm Page ___________________________

        self.alarm_timeEdit = self.findChild(QTimeEdit, "alarm_timeEdit")
        self.set_alarm_pushButton = self.findChild(QPushButton, "set_alarm_pushButton")
        self.alarm_status_label = self.findChild(QLabel, "alarm_status_label")

        self.alarm_time = None
        self.alarm_active = False
        self.alarm_sound = QSound("assets/alarm.wav")
        self.set_alarm_pushButton.clicked.connect(self.set_alarm)

        # Timer to check alarm every second
        self.check_alarm_timer = QTimer()
        self.check_alarm_timer.timeout.connect(self.check_alarm)
        self.check_alarm_timer.start(1000)



        # ___________________________ Timer Page ___________________________

        self.timer_label = self.findChild(QLabel, "label")
        self.start_pushButton = self.findChild(QPushButton, "start_pushButton")
        self.stop_pushButton = self.findChild(QPushButton, "stop_pushButton")
        self.resume_pushButton = self.findChild(QPushButton, "resume_pushButton")
        self.hour_spinbox = self.findChild(QSpinBox, "hour_spinBox")
        self.minute_spinbox = self.findChild(QSpinBox, "minute_spinBox")
        self.minute_spinbox.setMaximum(59)

        self.remaining_seconds = 0

        # Timer countdown logic
        self.countdown_timer = QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)

        self.start_pushButton.clicked.connect(self.start_countdown)
        self.stop_pushButton.clicked.connect(self.stop_countdown)
        self.resume_pushButton.clicked.connect(self.resume_countdown)

        # Sound for timer alert
        self.timer_sound = QSound("assets/alarm.wav")



        # ___________________________ Stopwatch Page ___________________________

        self.stopwatch_label = self.findChild(QLabel, "stopwatch_label")
        self.stopwatch_start_pushButton = self.findChild(QPushButton, "stopwatch_start_pushButton")
        self.stopwatch_stop_pushButton = self.findChild(QPushButton, "stopwatch_stop_pushButton")
        self.stopwatch_reset_pushButton = self.findChild(QPushButton, "stopwatch_reset_pushButton")

        self.stopwatch_seconds = 0

        # Stopwatch timer
        self.stopwatch_timer = QTimer()
        self.stopwatch_timer.timeout.connect(self.update_stopwatch)

        self.stopwatch_start_pushButton.clicked.connect(self.start_stopwatch)
        self.stopwatch_stop_pushButton.clicked.connect(self.stop_stopwatch)
        self.stopwatch_reset_pushButton.clicked.connect(self.reset_stopwatch)



        # ___________________________ Real-Time Clock ___________________________

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)
        self.update_clock()


        self.show()




    # ====================================================
    #                   Clock Functions
    # ====================================================

    def update_clock(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%I:%M:%S %p"))
        self.date_label.setText(now.strftime("%Y/%m/%d"))



    # ====================================================
    #                   Timer Functions
    # ====================================================

    def start_countdown(self):
        hours = self.hour_spinbox.value()
        minutes = self.minute_spinbox.value()
        total_seconds = (hours * 3600) + (minutes * 60)

        self.remaining_seconds = total_seconds
        self.update_countdown()
        self.countdown_timer.start(1000)


    def stop_countdown(self):
        self.countdown_timer.stop()
       

    def resume_countdown(self):
        self.countdown_timer.start(1000)


    def update_countdown(self):
        if self.remaining_seconds > 0:
            mins, secs = divmod(self.remaining_seconds, 60)
            hours, mins = divmod(mins, 60)
            self.timer_label.setText(f"{hours:02d}:{mins:02d}:{secs:02d}")
            self.remaining_seconds -= 1
        else:
            self.countdown_timer.stop()
            self.timer_label.setText("Time is up!")

            # Play sound and show message when time is up
            self.timer_sound.play()
            msg = QMessageBox(self)
            msg.setWindowTitle("Timer Finished")
            msg.setText("Your countdown has ended!")
            ok_btn = msg.addButton("OK", QMessageBox.AcceptRole)
            msg.exec_()
            self.timer_sound.stop()



    # ====================================================
    #                   Alarm Functions
    # ====================================================

    def set_alarm(self):
        self.alarm_time = self.alarm_timeEdit.time()
        self.alarm_active = True
        self.alarm_status_label.setText(f" Alarm set for {self.alarm_time.toString('HH:mm')}")


    def check_alarm(self):
        if self.alarm_active:
            now = QTime.currentTime()
            if now.hour() == self.alarm_time.hour() and now.minute() == self.alarm_time.minute():
                self.trigger_alarm()


    def trigger_alarm(self):
        self.alarm_active = False
        self.alarm_sound.play()

        msg = QMessageBox(self)
        msg.setWindowTitle("Alarm")
        msg.setText(f"It's now {self.alarm_time.toString('HH:mm')}. Wake up!")

        snooze_btn = msg.addButton("Snooze 5 min", QMessageBox.ActionRole)
        stop_btn = msg.addButton("Stop", QMessageBox.RejectRole)

        msg.exec_()
        self.alarm_sound.stop()

        if msg.clickedButton() == snooze_btn:
            self.alarm_time = self.alarm_time.addSecs(300)
            self.alarm_active = True
            self.alarm_status_label.setText(f"Alarm snoozed to {self.alarm_time.toString('HH:mm')}")
        elif msg.clickedButton() == stop_btn:
            self.alarm_status_label.setText("Alarm stopped")



    # ====================================================
    #                Stopwatch Functions
    # ====================================================

    def start_stopwatch(self):
        self.stopwatch_timer.start(1000)


    def stop_stopwatch(self):
        self.stopwatch_timer.stop()


    def reset_stopwatch(self):
        self.stopwatch_timer.stop()
        self.stopwatch_seconds = 0
        self.stopwatch_label.setText("00:00:00")


    def update_stopwatch(self):
        self.stopwatch_seconds += 1
        mins, secs = divmod(self.stopwatch_seconds, 60)
        hours, mins = divmod(mins, 60)
        self.stopwatch_label.setText(f"{hours:02d}:{mins:02d}:{secs:02d}")





# ___________________________ Run Application ___________________________

app = QApplication(sys.argv)
window = UI()
app.exec_()
