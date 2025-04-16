import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTabWidget,
    QMessageBox, QComboBox, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib
import matplotlib.pyplot as plt

# 한글 폰트 설정 (윈도우 기준)
matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False


class SensorDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("스마트 산업현장 대시보드")
        self.setGeometry(200, 200, 1000, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.sensors = ["temperature", "gas", "power", "sound"]

        # 위험 기준선 설정
        self.thresholds = {
            "temperature": 66,
            "gas": 200,
            "power": 4.0,
            "sound": 80
        }

        # 탭별 센서 추가
        for sensor in self.sensors:
            self.tabs.addTab(self.create_sensor_tab(sensor), sensor)

        # 타이머로 데이터 주기적 로딩
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all_tabs)
        self.timer.start(2000)

    def create_sensor_tab(self, sensor):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        figure = Figure()
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)

        self.sensor_label = QLabel(f"센서 종류: {sensor}")
        layout.addWidget(self.sensor_label)

        widget.canvas = canvas
        widget.figure = figure
        widget.sensor = sensor
        return widget

    def update_all_tabs(self):
        try:
            df = pd.read_csv("C:/Users/user/Desktop/산업재해데이터/sensor_result.csv", encoding="cp949")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            recent_data = df.tail(30)

            for i in range(self.tabs.count()):
                tab = self.tabs.widget(i)
                sensor = tab.sensor
                ax = tab.figure.clear()
                ax = tab.figure.add_subplot(111)
                ax.plot(recent_data['timestamp'], recent_data[sensor], label=sensor)

                # 기준선 추가
                if sensor in self.thresholds:
                    threshold = self.thresholds[sensor]
                    ax.axhline(y=threshold, color='red', linestyle='--', label=f"위험 기준: {threshold}")

                ax.set_title(f"{sensor} 실시간 추이")
                ax.set_xlabel("시간")
                ax.set_ylabel("값")
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True)
                ax.legend()
                tab.canvas.draw()

            # 경고 감지
            latest = df.iloc[-1]
            if latest['temperature'] >= 66:
                self.show_alert("온도 경고", f"온도 초과: {latest['temperature']}°C")
            if latest['sound'] >= 85:
                self.show_alert("소음 경고", f"소음 초과: {latest['sound']}dB")
            if latest['gas'] >= 200:
                self.show_alert("가스 경고", f"가스 농도 초과: {latest['gas']}ppm")

        except Exception as e:
            print(f"[에러] {e}")

    def show_alert(self, title, message):
        alert = QMessageBox()
        alert.setWindowTitle(title)
        alert.setText(message)
        alert.setIcon(QMessageBox.Warning)
        alert.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = SensorDashboard()
    dashboard.show()
    sys.exit(app.exec_())
