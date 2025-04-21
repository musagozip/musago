import os
import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTabWidget,
    QMessageBox, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QFrame, QDialog, QDialogButtonBox, QGridLayout,QScrollArea,QSizePolicy
)
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import matplotlib
import matplotlib.pyplot as plt
import pymysql
import subprocess
from datetime import datetime

matplotlib.rcParams['font.family'] = 'Malgun Gothic'
matplotlib.rcParams['axes.unicode_minus'] = False

class SensorDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("스마트 산업현장 에너지·안전 대시보드")
        self.setGeometry(200, 200, 1100, 720)
        self.simulator_process_cpp = None
        self.simulator_process_py = None

        self.csv_path = "C:/Users/user/Desktop/산업재해데이터/sensor_result.csv"
        self.df = pd.read_csv(self.csv_path, encoding="cp949")
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.last_row_count = len(self.df)
        self.simulator_process = None
        self.alert_active = True



        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        title = QLabel("스마트 산업현장 실시간 모니터링")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px; background-color: #f44336; color: white;")
        self.layout.addWidget(title)

        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ 시뮬레이터 실행")
        self.stop_btn = QPushButton("■ 시뮬레이터 종료")
        self.status_label = QLabel("상태: 시뮬레이터 중지됨")
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.status_label)
        self.layout.addLayout(button_layout)

        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #e53935;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """) 
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #616161;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #424242;
            }
        """)

        self.start_btn.clicked.connect(self.start_simulator)
        self.stop_btn.clicked.connect(self.stop_simulator)

        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        self.sensors = ["temperature", "gas", "power", "sound"]
        self.thresholds = {
            "temperature": 66,
            "gas": 200,
            "power": 4.0,
            "sound": 80
        }

        for sensor in self.sensors:
            self.tabs.addTab(self.create_sensor_tab(sensor), sensor)
        
        # __init__() 마지막 탭 구성 부분에 추가하세요
        # __init__에서 탭 추가할 때
        self.efficiency_csv_path = "C:/Users/user/Desktop/산업재해데이터/에너지_효율_실시간.csv"
        self.efficiency_tab = self.create_efficiency_tab()
        self.efficiency_tab_index = self.tabs.addTab(self.efficiency_tab, "전력 효율 데이터")


        self.tabs.addTab(self.create_event_log_tab(), "이벤트 로그")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all_tabs)
        self.timer.start(2000)

    def start_simulator(self):
        if not self.simulator_process:
            try:
                self.simulator_process = subprocess.Popen(
                    ["C:/Users/user/Desktop/산업재해데이터/run_and_sync/musago.exe"]
                )
                self.simulator_process_py = subprocess.Popen(
                    ["python","C:/Users/user/Documents/python_db_connect/sensor_simulator.py" ], cwd=os.path.dirname(__file__)
                )
                self.status_label.setText("상태: 실행 중")
                self.start_btn.setEnabled(False)
                self.alert_active = True
                print("▶ 센서 시뮬레이터 실행됨")
            except Exception as e:
                print(f"[시뮬레이터 실행 오류] {e}")

    def stop_simulator(self):
        if self.simulator_process:
            self.simulator_process.terminate()
            self.simulator_process = None
            self.status_label.setText("상태: 시뮬레이터 중지됨")
            self.start_btn.setEnabled(True)
            self.alert_active = False
            print("⏹ 센서 시뮬레이터 종료됨")
            if self.simulator_process_cpp:
                self.simulator_process_cpp.terminate()
                self.simulator_process_cpp = None
            if self.simulator_process_py:
                self.simulator_process_py.terminate()
                self.simulator_process_py = None

    def create_sensor_tab(self, sensor):
        frame = QFrame()
        layout = QVBoxLayout()
        frame.setLayout(layout)

        figure = Figure()
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)

        sensor_label = QLabel(f"센서 종류: {sensor}")
        layout.addWidget(sensor_label)

        frame.canvas = canvas
        frame.figure = figure
        frame.sensor = sensor
        return frame

    def create_event_log_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.event_table = QTableWidget()
        self.event_table.setColumnCount(6)
        self.event_table.setHorizontalHeaderLabels(["시간", "온도", "가스", "전력", "소음", "위험 등급"])
        layout.addWidget(self.event_table)

        self.load_event_log()
        return widget

    def load_event_log(self):
        try:
            conn = pymysql.connect(
                host='localhost',
                user='root',
                password='1234',
                database='musago_db',
                charset='utf8mb4'
            )
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, temperature, gas, power, sound, risk FROM event_log ORDER BY id DESC LIMIT 100")
            rows = cursor.fetchall()
            self.event_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row):
                    self.event_table.setItem(i, j, QTableWidgetItem(str(val)))
            conn.close()
        except Exception as e:
            print(f"[DB 이력 조회 오류] {e}")

    def update_all_tabs(self):
        try:
            new_df = pd.read_csv(self.csv_path, encoding="cp949")
            new_df['timestamp'] = pd.to_datetime(new_df['timestamp'])

            new_data_added = False
            latest = None

            if len(new_df) > self.last_row_count:
                new_rows = new_df.iloc[self.last_row_count:]
                self.df = pd.concat([self.df, new_rows], ignore_index=True)
                self.last_row_count = len(new_df)

                latest = self.df.iloc[-1]
                new_data_added = True  # 플래그 설정
                self.update_efficiency_tab()

                # DB 저장
                try:
                    conn = pymysql.connect(
                        host='localhost',
                        user='root',
                        password='1234',
                        database='musago_db',
                        charset='utf8mb4'
                    )
                    cursor = conn.cursor()

                    cursor.execute('''
                        INSERT INTO sensor_data (timestamp, temperature, gas, power, sound, risk)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (
                        latest['timestamp'], latest['temperature'], latest['gas'],
                        latest['power'], latest['sound'], latest['risk']
                    ))

                    if str(latest['risk']).strip() != "정상":
                        cursor.execute('''
                            INSERT INTO event_log (timestamp, temperature, gas, power, sound, risk)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        ''', (
                            latest['timestamp'], latest['temperature'], latest['gas'],
                            latest['power'], latest['sound'], latest['risk']
                        ))

                    conn.commit()
                    conn.close()
                except Exception as e:
                    print(f"[DB 저장 오류] {e}")

            # 시각화
            recent_data = self.df.tail(50)
            self.load_event_log()

            for i in range(len(self.sensors)):
                tab = self.tabs.widget(i)
                sensor = tab.sensor
                ax = tab.figure.clear()
                ax = tab.figure.add_subplot(111)
                ax.plot(recent_data['timestamp'], recent_data[sensor], label=sensor)

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

            # 알림은 new_data_added일 때만 작동
            if self.alert_active and new_data_added:
                if latest['temperature'] >= self.thresholds["temperature"]:
                    self.show_custom_alert("온도 경고", f"온도 초과: {latest['temperature']}°C")
                if latest['sound'] >= self.thresholds["sound"]:
                    self.show_custom_alert("소음 경고", f"소음 초과: {latest['sound']}dB")
                if latest['gas'] >= self.thresholds["gas"]:
                    self.show_custom_alert("가스 경고", f"가스 농도 초과: {latest['gas']}ppm")

        except Exception as e:
            print(f"[실시간 그래프 에러] {e}")


    def update_efficiency_tab(self):
        try:
            df_eff = pd.read_csv(self.efficiency_csv_path, encoding="cp949")
            df_eff['timestamp'] = pd.to_datetime(df_eff['timestamp'])

            scroll_area = self.efficiency_tab  # 직접 참조
            content = scroll_area.widget()
            if not content:
                return

            layout = content.layout()
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            for metric in ["temperature", "humidity", "co2", "power_usage", "efficiency(%)"]:
                fig = Figure(figsize=(10, 2.5))
                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                ax = fig.add_subplot(111)
                ax.plot(df_eff['timestamp'], df_eff[metric], label=metric)
                ax.set_title(f"{metric} 추이")
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True)
                ax.legend()
                layout.addWidget(canvas)

        except Exception as e:
            print(f"[전력 효율 실시간 업데이트 오류] {e}")


  

    def create_efficiency_tab(self):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)
        scroll_area.setWidget(content_widget)

        try:
            df = pd.read_csv(self.efficiency_csv_path, encoding="cp949")
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            for metric in ["temperature", "humidity", "co2", "power_usage", "efficiency(%)"]:
                fig = Figure(figsize=(10, 2.5))
                canvas = FigureCanvas(fig)
                canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                ax = fig.add_subplot(111)
                ax.plot(df['timestamp'], df[metric], label=metric)
                ax.set_title(f"{metric} 추이")
                ax.tick_params(axis='x', rotation=45)
                ax.grid(True)
                ax.legend()
                content_layout.addWidget(canvas)

        except Exception as e:
            label = QLabel(f"[에러] 전력 효율 데이터 로딩 실패: {e}")
            content_layout.addWidget(label)

        scroll_area.setWidget(content_widget)
        return scroll_area



    def show_custom_alert(self, title, message):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setStyleSheet("background-color: #fff3f3; border: 1px solid #e53935;")
        layout = QVBoxLayout()
        label = QLabel(message)
        label.setStyleSheet("color: #d32f2f; font-weight: bold;")
        layout.addWidget(label)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(dialog.accept)
        layout.addWidget(buttons)
        dialog.setLayout(layout)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = SensorDashboard()
    dashboard.show()
    sys.exit(app.exec_())
