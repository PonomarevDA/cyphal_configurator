#!/usr/bin/env python3.7
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSlider, QVBoxLayout, QHBoxLayout, QGridLayout, QSpinBox, QHBoxLayout
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer, QThread
from configurator import ServerNodeFrontend


NUMBER_OF_ESC = 4


class EscWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        self.setMinimumHeight(400)
        sub_layout = QHBoxLayout(self)
        sub_layout.addStretch()
        sub_layout.addStretch()
        layout.addLayout(sub_layout)
        self.setLayout(layout)

        self._slider = QSlider(Qt.Vertical, self)
        self._slider.setMinimum(-100)
        self._slider.setMaximum(100)
        self._slider.setValue(0)
        self._slider.setTickInterval(100)
        self._slider.setTickPosition(QSlider.TicksBothSides)
        self._slider.valueChanged.connect(lambda: self._spinbox.setValue(self._slider.value()))
        sub_layout.addWidget(self._slider)

        self._spinbox = QSpinBox(self)
        self._spinbox.setMinimum(-100)
        self._spinbox.setMaximum(100)
        self._spinbox.setValue(0)
        self._spinbox.valueChanged.connect(lambda: self._slider.setValue(self._spinbox.value()))
        layout.addWidget(self._spinbox)

        self._voltage = QLabel()
        layout.addWidget(self._voltage)
        self.set_voltage()

        self._current = QLabel()
        layout.addWidget(self._current)
        self.set_current()

        self._readiness = QLabel()
        layout.addWidget(self._readiness)
        self.set_readiness()

        self._health = QLabel()
        layout.addWidget(self._health)
        self.set_health()

        self._demand_factor = QLabel()
        layout.addWidget(self._demand_factor)
        self.set_demand_factor()
        
    def get_setpoint(self):
        return self._slider.value()

    def set_voltage(self, value=None):
        value_str = str()
        if value is None:
            value_str = "-"
        else:
            value_str = "{:.1f}".format(value)
        self._voltage.setText("power.voltage: {} V".format(value_str))

    def set_current(self, value=None):
        value_str = str()
        if value is None:
            value_str = "-"
        else:
            value_str = "{:.3f}".format(value)
        self._current.setText("power.current: {} A".format(value_str))

    def set_readiness(self, value_str=None):
        if value_str is None:
            value_str = "-"
        self._readiness.setText("feedback.readiness: {}".format(value_str))

    def set_health(self, value_str=None):
        if value_str is None:
            value_str = "-"
        self._health.setText("feedback.health: {}".format(value_str))

    def set_demand_factor(self, value_str=None):
        if value_str is None:
            value_str = "-"
        self._demand_factor.setText("feedback.demand_factor: {} %".format(value_str))


class EscPanel(QWidget):
    def __init__(self, server_node):
        super().__init__()
        self.server_node = server_node.server_node
        self.setWindowTitle('Esc Panel')

        self.layout = QGridLayout(self)
        self.layout.setSpacing(10)

        self.channels = []
        for channel_idx in range(NUMBER_OF_ESC):
            esc = EscWidget()
            self.channels.append(esc)
            self.layout.addWidget(esc, 0, channel_idx)

        self.setLayout(self.layout)

        self.feedback_timer = QTimer()
        self.feedback_timer.timeout.connect(self.timer_event)
        self.feedback_timer.start(1000)

    def timer_event(self):
        self.feedback_timer.start(10)

        self.channels[0].set_voltage(self.server_node.get_voltage())
        self.channels[0].set_current(self.server_node.get_current())
        self.channels[0].set_readiness(self.server_node.get_readiness())
        self.channels[0].set_health(self.server_node.get_health())
        self.channels[0].set_demand_factor(self.server_node.get_demand_factor_pct())
        self.server_node.set_setpoint(self.channels[0].get_setpoint() / 100)


class ServerNodeThread(QThread):
    mysignal = QtCore.pyqtSignal(str)
    def  __init__(self, parent=None):
        QThread.__init__(self, parent)
        self.server_node = ServerNodeFrontend()
    def run(self):
        self.server_node.run_async()


def create_esc_panel():
    app = QApplication(sys.argv)

    server_node = ServerNodeThread()
    server_node.start()

    window = EscPanel(server_node)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    create_esc_panel()
