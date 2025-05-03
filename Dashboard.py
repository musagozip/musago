import sys
import os
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTabWidget,
    QTableWidget, QTableWidgetItem, QSizePolicy, QPushButton, QHBoxLayout,
    QFrame, QGridLayout, QScrollArea, QHeaderView
)
from PyQt5.QtCore import QTimer, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import subprocess
import time
from PyQt5.QtGui import QFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from io import BytesIO
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog
import numpy as np
import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
pdfmetrics.registerFont(TTFont('NanumGothic', "C:/Users/user/Desktop/데이터 수정/최종프로젝트/Nanum_Gothic/NanumGothic-Regular.ttf"))

# 파일 시스템 관련 인코딩 설정
if sys.platform.startswith('win'):
    # Windows에서 한글 파일 경로를 위한 설정
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class RealtimePredictDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("실시간 예측 통합 대시보드")
        self.setGeometry(200, 200, 1300, 850)  # 높이를 850으로 증가
        self.stats_tabs = {}
        # 폰트 설정
        self.setup_fonts()
        self.main_script_path = "C:/Users/user/Desktop/데이터 수정/최종프로젝트/python/main_auto_predictor.py"
        self.index = 0
        self.max_rows = 0
        self.main_process = None
        self.processing_data = False
        self.start_time = None
        self.prediction_status = {
            "위험 예측": False,
            "고장 예측": False,
            "복합 위험 등급": False,
            "이상치 탐지": False,
            "에너지 예측": False
        }
        
        # 센서 임계값 설정
        self.sensor_thresholds = {
            "temperature": {"threshold": 30, "operator": ">=", "icon": "🌡", "name": "온도", "unit": "°C"},
            "humidity": {"threshold": 32, "operator": "<=", "icon": "💧", "name": "습도", "unit": "%"},
            "co2": {"threshold": 1000, "operator": ">=", "icon": "☁️", "name": "CO2", "unit": "ppm"},
            "vibration": {"threshold": 5.0, "operator": ">=", "icon": "📳", "name": "진동", "unit": "Hz"}
        }
        
        # 모든 예측 결과 파일 경로
        self.base_dir = "C:/Users/user/Desktop/데이터 수정/최종프로젝트"
        
        # 모든 예측 결과 파일 경로
        self.sensor_path = os.path.join(self.base_dir, "shared/data/sensor_result.csv")
        
        # 각 예측 결과 파일의 경로도 base_dir 기준으로 설정
        self.prediction_paths = {
            "이상치 탐지": os.path.join(self.base_dir, "shared/data/anomaly_prediction.csv"),
            "위험 예측": os.path.join(self.base_dir, "shared/data/risk_prediction.csv"),
            "복합 위험 등급": os.path.join(self.base_dir, "shared/data/risk_level_prediction.csv"),
            "고장 예측": os.path.join(self.base_dir, "shared/data/fault_prediction.csv"),
            "에너지 예측": os.path.join(self.base_dir, "shared/data/energy_prediction.csv")
        }
        
        # 예측 상태에 사용할 아이콘 매핑
        self.status_icons = {
            "위험 예측": "🧠",
            "고장 예측": "🛠",
            "복합 위험 등급": "📊",
            "이상치 탐지": "🚨",
            "에너지 예측": "⚡"
        }

        self.sensor_df = pd.DataFrame()
        self.predictions = {}
        self.initial_file_timestamps = {}
        
        # 센서 상태 카드 레이블
        self.sensor_status_cards = {}

        # 레이아웃 구성
        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel("🔍 실시간 센서 및 예측 대시보드")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px; background-color: #f44336; color: white;")
        layout.addWidget(title)

        # 상태 표시 레이블
        self.status_label = QLabel("상태: 시뮬레이터 중지됨")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #616161;")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 세부 예측 상태 레이블
        self.prediction_status_label = QLabel("")
        self.prediction_status_label.setStyleSheet("font-size: 13px; padding: 3px; color: #424242;")
        self.prediction_status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.prediction_status_label)

        # 실행/정지/PDF 내보내기 버튼
        self.btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("▶ 실행")
        self.stop_btn = QPushButton("■ 종료")
        self.export_pdf_btn = QPushButton("📄 PDF 출력")
        
        self.start_btn.clicked.connect(self.start_stream)
        self.stop_btn.clicked.connect(self.stop_stream)
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)
        
        self.btn_layout.addWidget(self.start_btn)
        self.btn_layout.addWidget(self.stop_btn)
        self.btn_layout.addWidget(self.export_pdf_btn)
        
        layout.addLayout(self.btn_layout)

        # 버튼 스타일 설정
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
        self.export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)

        self.tabs = QTabWidget()

        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ccc;
                top: -1px;
            }
            QTabBar::tab {
                background: #eeeeee;
                border: 1px solid #ccc;
                border-bottom-color: #999;
                padding: 8px 18px;
                font-weight: bold;
                color: #333;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background: #e53935;
                color: white;
                border: 2px solid #e53935;
                border-bottom: none;
            }
            QTabBar::tab:hover {
                background: #f44336;
                color: white;
            }
        """)

        layout.addWidget(self.tabs)

        self.sensor_tab = None
        self.prediction_tabs = {}

        # 타이머 (초기 정지 상태)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_tables)
        
        # 데이터 처리 확인 타이머
        self.processing_timer = QTimer()
        self.processing_timer.timeout.connect(self.check_data_processing)
    
    def export_to_pdf(self):
        """대시보드의 현재 데이터와 그래프를 PDF로 내보내기"""
        # PDF 저장 위치 선택
        options = QFileDialog.Options()
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"대시보드_리포트_{now}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self, "PDF 저장", default_name, "PDF 파일 (*.pdf)", options=options
        )
        
        if not file_path:
            return  # 사용자가 취소했을 경우
            
        # PDF 생성 시작
        self.status_label.setText("상태: PDF 생성 중...")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #2196f3;")
        
        try:
            # PDF 문서 생성
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=1*cm,
                leftMargin=1*cm,
                topMargin=1*cm,
                bottomMargin=1*cm
            )
            
            # 스타일 설정
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Title'],
                fontName='NanumGothic',
                fontSize=16,
                leading=20,
                alignment=1,  # 중앙 정렬
                spaceAfter=12
            )
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=styles['Heading2'],
                fontName='NanumGothic',
                fontSize=14,
                leading=18,
                alignment=0,  # 왼쪽 정렬
                spaceBefore=10,
                spaceAfter=8
            )
            normal_style = ParagraphStyle(
                'Normal',
                parent=styles['Normal'],
                fontName='NanumGothic',   # ✅ 추가
                fontSize=11,
                leading=14,
                spaceAfter=6
            )
            
            # PDF에 들어갈 요소들
            elements = []
            
            # 제목 및 날짜
            elements.append(Paragraph(f"실시간 예측 통합 대시보드 리포트", title_style))
            elements.append(Paragraph(f"생성 일시: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
            elements.append(Spacer(1, 0.5*cm))
            
            # 1. 센서 데이터 섹션
            elements.append(Paragraph("1. 센서 데이터 현황", subtitle_style))
            
            # 센서 데이터 테이블 추가 (최신 10개 행만)
            if not self.sensor_df.empty:
                sensor_data = self.sensor_df.tail(10).values.tolist()
                sensor_headers = self.sensor_df.columns.tolist()
                
                # 테이블 헤더 추가
                sensor_data.insert(0, sensor_headers)
                
                # 열 너비 계산 - A4 너비에 맞추기
                available_width = A4[0] - 2*cm  # A4 너비에서 좌우 마진 제외
                col_count = len(sensor_headers)
                col_widths = [available_width/col_count] * col_count
                
                # 테이블 생성 (열 너비 지정)
                table = Table(sensor_data, repeatRows=1, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('WORDWRAP', (0, 0), (-1, -1), True),  # 텍스트 자동 줄바꿈
                ]))
                elements.append(table)
                elements.append(Spacer(1, 0.3*cm))
            
            # 센서 그래프 추가
            elements.append(Paragraph("센서 그래프", normal_style))
            sensor_names = ["temperature", "humidity", "co2", "vibration"]
            
            for sensor in sensor_names:
                if hasattr(self, 'sensor_tab') and sensor in self.sensor_tab["figures"]:
                    # 그래프를 이미지로 변환
                    fig = self.sensor_tab["figures"][sensor]["figure"]
                    fig.tight_layout()           # 🔹 여백 확보
                    fig.canvas.draw()
                    img_data = BytesIO()
                    fig.savefig(img_data, format='png', dpi=150, bbox_inches='tight')
                    img_data.seek(0)
                    
                    # 이미지 크기 조정 (A4 너비에 맞춤)
                    img = Image(img_data, width=7*inch, height=3*inch)
                    elements.append(Spacer(1, 0.2*cm))
                    elements.append(img)
                    elements.append(Spacer(1, 0.5*cm))
            
            
            # 2. 예측 결과 섹션
            elements.append(Paragraph("2. 예측 결과", subtitle_style))

            # 각 예측 탭의 데이터와 그래프 추가
            for label, tab in self.prediction_tabs.items():
                elements.append(Paragraph(f"{label} 결과", normal_style))
                
                # 해당 예측의 데이터프레임이 존재하면 추가
                if label in self.predictions and not self.predictions[label].empty:
                    fig = tab["figure"]
                    fig.tight_layout()
                    fig.canvas.draw()

                    img_data = BytesIO()
                    fig.savefig(img_data, format='png', dpi=150, bbox_inches='tight')  # 🔹 fix here
                    img_data.seek(0)
                    img = Image(img_data, width=7*inch, height=3*inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.5*cm))
                    
                    # 여기서 테이블 생성 부분을 제거하고 그래프만 추가
                    # 해당 탭의 그래프 추가
                    # if hasattr(tab, 'figure'):
                    #     fig = tab["figure"]
                    #     fig.tight_layout()
                    #     fig.canvas.draw()
                    #     img_data = BytesIO()
                    #     fig.savefig(img_data, format='png', dpi=150, bbox_inches='tight')
                    #     # tab["figure"].savefig(img_data, format='png', dpi=150, bbox_inches='tight')
                    #     img_data.seek(0)
                    #     img = Image(img_data, width=7*inch, height=3*inch)
                    #     elements.append(img)
                    #     elements.append(Spacer(1, 0.5*cm))
            
            # 3. 예측 통계 요약 섹션
            elements.append(Paragraph("3. 예측 통계 요약", subtitle_style))
            
            # 위험 예측 분포 파이 차트
            if "예측 통계 요약" in self.stats_tabs:
                stats_tab = self.stats_tabs["예측 통계 요약"]
                
                # 통계 테이블 데이터 추출
                stats_table = stats_tab["stats_table"]
                table_data = []
                table_data.append(["카테고리", "개수"])
                
                for row in range(stats_table.rowCount()):
                    category = stats_table.item(row, 0).text()
                    count = stats_table.item(row, 1).text()
                    table_data.append([category, count])
                
                # 테이블 생성
                table = Table(table_data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'NanumGothic'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 0.3*cm))
                
                # 파이 차트 추가
                img_data = BytesIO()
                stats_tab["risk_figure"].savefig(img_data, format='png', dpi=150, bbox_inches='tight')
                img_data.seek(0)
                img = Image(img_data, width=6*inch, height=4*inch)
                elements.append(img)
            
            # PDF 생성
            doc.build(elements)
            
            # 성공 메시지 표시
            self.status_label.setText(f"상태: PDF 생성 완료 ({file_path})")
            self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #4caf50;")
            
        except Exception as e:
            print(f"PDF 생성 중 오류 발생: {e}")
            self.status_label.setText(f"상태: PDF 생성 실패")
            self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #f44336;")

    def setup_fonts(self):
        """폰트 설정 및 확인"""
        # 선호하는 글꼴 목록
        preferred_fonts = ['Malgun Gothic', 'NanumGothic', 'NanumBarunGothic', 'Gulim', 'Dotum']
        
        # 사용 가능한 폰트 찾기
        available_font = None
        for font in preferred_fonts:
            try:
                fp = FontProperties(family=font)
                if fp.get_family()[0] != 'sans-serif':  # 폰트가 실제로 존재하는지 확인
                    available_font = font
                    break
            except:
                continue
                
        # 사용할 폰트 설정
        if available_font:
            matplotlib.rcParams['font.family'] = [available_font, 'Segoe UI Emoji', 'DejaVu Sans']
        else:
            # 대체 방법: 기본 폰트 사용
            matplotlib.rcParams['font.family'] = ['DejaVu Sans', 'Segoe UI Emoji']
            
        # 음수 기호 깨짐 방지
        matplotlib.rcParams['axes.unicode_minus'] = False
        # 기본 폰트 크기 설정
        plt.rcParams['font.size'] = 10

    def print_status(self, message):
        """상태 메시지 출력 (콘솔용)"""
        try:
            print(message)
        except UnicodeEncodeError:
            # 이모지나 한글이 포함된 경우 대체 메시지 출력
            simplified_msg = ''.join(c if ord(c) < 128 else '?' for c in message)
            print(simplified_msg)

    def get_file_timestamps(self):
        """현재 존재하는 모든 파일의 마지막 수정 시간을 저장"""
        timestamps = {}
        
        if os.path.exists(self.sensor_path):
            timestamps[self.sensor_path] = os.path.getmtime(self.sensor_path)
            
        for label, path in self.prediction_paths.items():
            if os.path.exists(path):
                timestamps[path] = os.path.getmtime(path)
                
        return timestamps
    
    def update_prediction_status_label(self):
        """예측 상태 레이블 업데이트"""
        if not self.processing_data:
            self.prediction_status_label.setText("")
            return
            
        status_text = ""
        all_done = True
        
        for label, completed in self.prediction_status.items():
            icon = self.status_icons[label]
            if completed:
                status_text += f"{icon} {label}: ✓  "
            else:
                status_text += f"{icon} {label}: 처리 중...  "
                all_done = False
                
        if all_done:
            status_text = "✅ 모든 예측 완료!"
            
        self.prediction_status_label.setText(status_text)
        
    def check_data_processing(self):
        """데이터 처리 상태 확인"""
        if not self.processing_data:
            return
            
        # 디렉토리가 존재하는지 확인
        shared_data_dir = os.path.join(self.base_dir, "shared/data")
        if not os.path.exists(shared_data_dir):
            self.print_status(f"경고: 데이터 디렉토리가 없습니다: {shared_data_dir}")
            return
                
        current_timestamps = self.get_file_timestamps()
        
        # 각 예측 파일별 업데이트 확인
        for label, path in self.prediction_paths.items():
            if path in current_timestamps:
                # 파일이 존재하고 초기 타임스탬프보다 새로운 경우 (또는 초기에 없었던 경우)
                if path not in self.initial_file_timestamps or current_timestamps[path] > self.initial_file_timestamps[path]:
                    self.prediction_status[label] = True
                    self.print_status(f"✅ {label} 업데이트 감지됨")
        
        # 예측 상태 레이블 업데이트
        self.update_prediction_status_label()
        
        # 모든 예측이 완료되었는지 확인
        all_predictions_done = all(self.prediction_status.values())
        
        # 센서 데이터가 업데이트되었는지 확인
        sensor_updated = (self.sensor_path in current_timestamps and 
                        (self.sensor_path not in self.initial_file_timestamps or 
                        current_timestamps[self.sensor_path] > self.initial_file_timestamps[self.sensor_path]))
        
        # 충분한 시간이 경과했고 조건이 충족되면 시각화 시작
        if (time.time() - self.start_time >= 10):
            # 센서 파일이 있고 모든 예측이 완료된 경우에만 시각화 시작
            if os.path.exists(self.sensor_path) and all_predictions_done:
                self.processing_data = False
                self.processing_timer.stop()
                
                # 데이터 로드
                self.load_data()
                
                # UI 탭 구성
                self.setup_tabs()
                
                # 시각화 시작
                self.status_label.setText("상태: ✅ 실시간 시각화 진행 중")
                self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #2e7d32;")
                self.timer.start(1000)
                self.print_status("✅ 실시간 시각화 시작됨")
            elif os.path.exists(self.sensor_path) and not all_predictions_done:
                # 센서 파일은 있지만 예측이 모두 완료되지 않은 경우
                elapsed = int(time.time() - self.start_time)
                self.status_label.setText(f"상태: ⏳ 예측 처리 중... ({elapsed}초 경과)")
                self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #ff9800;")
            else:
                # 30초 이상 경과했는데도 센서 파일이 없으면 경고
                if (time.time() - self.start_time >= 30):
                    self.status_label.setText("상태: ⚠️ 센서 데이터 파일을 찾을 수 없습니다")
                    self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #ff9800;")
                    self.print_status(f"⚠️ 센서 데이터 파일이 없습니다: {self.sensor_path}")

    def load_data(self):
        """새로 생성된 데이터만 로드"""
        try:
            if os.path.exists(self.sensor_path):
                self.sensor_df = pd.read_csv(self.sensor_path, encoding="utf-8-sig")
                self.max_rows = len(self.sensor_df)
                self.print_status(f"센서 데이터 로드 완료: {len(self.sensor_df)}행")
            else:
                self.sensor_df = pd.DataFrame()
                self.print_status(f"센서 데이터 파일을 찾을 수 없음: {self.sensor_path}")

            self.predictions = {}
            for key, path in self.prediction_paths.items():
                if os.path.exists(path):
                    self.predictions[key] = pd.read_csv(path, encoding="utf-8-sig")
                    self.print_status(f"{key} 데이터 로드 완료: {len(self.predictions[key])}행")
                else:
                    self.predictions[key] = pd.DataFrame()  # 파일이 없으면 빈 데이터프레임
                    self.print_status(f"{key} 데이터 파일을 찾을 수 없음: {path}")
        except Exception as e:
            self.print_status(f"데이터 로드 중 오류 발생: {str(e)}")
    def setup_tabs(self):
        """UI 탭 구성"""
        self.tabs.clear()
        
        # 센서 데이터 탭 생성 (기능 개선)
        self.sensor_tab = self.create_enhanced_sensor_tab()
        self.tabs.addTab(self.sensor_tab["widget"], "센서 데이터")

        self.prediction_tabs = {}
        for label, df in self.predictions.items():
            if not df.empty:
                columns = df.columns.tolist()
                tab = self.create_tab(columns, label)
                self.tabs.addTab(tab["widget"], label)
                self.prediction_tabs[label] = tab

        stats_tab = self.create_stats_summary_tab()
        self.tabs.addTab(stats_tab["widget"], "예측 통계 요약")
        self.stats_tabs["예측 통계 요약"] = stats_tab

    def create_enhanced_sensor_tab(self):
        """향상된 센서 데이터 탭 생성"""
        tab_widget = QWidget()
        
        # 스크롤 영역 생성
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(700)  # 스크롤 영역의 최소 높이 설정
        
        # 스크롤될 메인 위젯 생성
        scroll_content = QWidget()
        main_layout = QVBoxLayout(scroll_content)
        main_layout.setContentsMargins(10, 10, 10, 20)  # 좌, 상, 우, 하 여백
        main_layout.setSpacing(15)  # 위젯 간 간격
        
        # 테이블 위젯 생성
        table = QTableWidget()
        columns = self.sensor_df.columns.tolist()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.verticalHeader().setVisible(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        table.setMaximumHeight(150)  # 테이블 높이 제한
        main_layout.addWidget(table)
        
        # 센서 상태 카드 섹션 생성
        card_frame = QFrame()
        card_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 10px;
                margin: 5px;
            }
        """)
        card_layout = QGridLayout(card_frame)
        
        # 센서 카드 생성
        sensor_names = ["temperature", "humidity", "co2", "vibration"]
        self.sensor_status_cards = {}
        
        for idx, sensor in enumerate(sensor_names):
            card = QLabel()
            card.setAlignment(Qt.AlignCenter)
            card.setStyleSheet("""
                QLabel {
                    background-color: white;
                    border-radius: 5px;
                    padding: 10px;
                    font-size: 14px;
                    border: 1px solid #e0e0e0;
                }
            """)
            card_layout.addWidget(card, idx // 2, idx % 2)
            self.sensor_status_cards[sensor] = card
            
        main_layout.addWidget(card_frame)
        
        # 그래프 프레임 생성
        graphs_frame = QFrame()
        graphs_layout = QVBoxLayout(graphs_frame)
        graphs_layout.setSpacing(30)  # 그래프 간 간격 증가
        
        # 각 센서에 대한 그래프 생성
        sensor_figures = {}
        for sensor in sensor_names:
            figure = Figure(figsize=(8, 3.5), dpi=100)  # 높이를 2.8로 설정, DPI 명시적 지정
            # 여백 미리 설정
            # figure.subplots_adjust(bottom=0.25, top=0.9, left=0.1, right=0.95)
            canvas = FigureCanvas(figure)
            canvas.setMinimumHeight(250)
            graphs_layout.addWidget(canvas)
            sensor_figures[sensor] = {"figure": figure, "canvas": canvas}
            
        main_layout.addWidget(graphs_frame)
        main_layout.addStretch(1)  # 스크롤 영역 하단에 여유 공간 추가
        
        # 스크롤 영역에 메인 위젯 설정
        scroll_area.setWidget(scroll_content)
        
        # 탭 위젯에 스크롤 영역 추가
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.addWidget(scroll_area)
        
        return {
            "widget": tab_widget, 
            "table": table, 
            "figures": sensor_figures, 
            "columns": columns, 
            "label": "센서 데이터"
        }

    def create_tab(self, columns, label):
        tab_widget = QWidget()
        layout = QVBoxLayout()
        tab_widget.setLayout(layout)

        table = QTableWidget()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.verticalHeader().setVisible(False)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(table)

        figure = Figure(figsize=(8, 3), dpi=100)
        # 여백 미리 설정
        figure.subplots_adjust(bottom=0.2, top=0.9, left=0.1, right=0.95)
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
    
        return {"widget": tab_widget, "table": table, "figure": figure, "canvas": canvas, "columns": columns, "label": label}

    def start_stream(self):
        self.index = 0
        self.print_status("▶ 예측 메인 자동화 스크립트 실행 중...")
        
        # 상태 초기화
        for key in self.prediction_status:
            self.prediction_status[key] = False
        
        shared_data_dir = os.path.join(self.base_dir, "shared/data")
        if not os.path.exists(shared_data_dir):
            os.makedirs(shared_data_dir, exist_ok=True)
        
        # 현재 파일 타임스탬프 저장 (나중에 비교용)
        self.initial_file_timestamps = self.get_file_timestamps()
        self.start_time = time.time()
        
        # 상태 업데이트
        self.status_label.setText("상태: ⏳ 데이터 처리 중...")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #ff9800;")
        
        # 예측 메인 스크립트 실행
        try:
            # 예측 메인 스크립트 실행 (shell=True로 변경하고 경로를 따옴표로 감싸기)
            cmd = f'python "{self.main_script_path}"'
            if sys.platform.startswith('win'):
                self.main_process = subprocess.Popen(
                    cmd,
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.main_process = subprocess.Popen(
                    cmd,
                    shell=True
                )
        
            # 데이터 처리 중 상태로 설정
            self.processing_data = True
            
            # 세부 예측 상태 표시 초기화
            self.update_prediction_status_label()
            
            # 데이터 처리 확인 타이머 시작
            self.processing_timer.start(500)  # 0.5초마다 체크

        except Exception as e:
            self.status_label.setText(f"상태: 오류 발생 - {str(e)}")
            self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #f44336;")
            self.print_status(f"오류 발생: {str(e)}")

    def stop_stream(self):
        self.timer.stop()
        self.processing_timer.stop()
        self.processing_data = False
        
        # 세부 예측 상태 표시 초기화
        self.prediction_status_label.setText("")
        
        if self.main_process:
            self.main_process.terminate()
            self.main_process = None
            
        self.status_label.setText("상태: 시뮬레이터 중지됨")
        self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #616161;")
        self.print_status("■ 스트리밍 및 메인 프로세스 종료")

    def update_tables(self):
        if self.index >= self.max_rows:
            self.timer.stop()
            self.status_label.setText("상태: ⏹ 모든 데이터 출력 완료")
            self.status_label.setStyleSheet("font-size: 14px; font-weight: bold; padding: 5px; color: #616161;")
            self.print_status("⏹ 모든 데이터 출력 완료")
            return

        # 현재 행 가져오기
        sensor_row = self.sensor_df.iloc[self.index]
        
        # 테이블에 행 추가
        self.append_row(self.sensor_tab["table"], sensor_row)
        
        # 센서 상태 카드 업데이트
        self.update_sensor_status_cards(sensor_row)
        
        # 센서 그래프 업데이트
        self.update_sensor_graphs(self.sensor_df.iloc[:self.index+1])

        # 예측 탭 업데이트
        for label, df in self.predictions.items():
            if not df.empty and self.index < len(df):  # 인덱스가 데이터프레임 길이보다 작은지 확인
                row = df.iloc[self.index]
                tab = self.prediction_tabs[label]
                self.append_row(tab["table"], row)
                col_name = tab["columns"][-1]  # 마지막 열을 그래프로 시각화
                self.update_plot(tab["figure"], df.iloc[:self.index+1], df.columns[0], col_name)

        self.update_prediction_stats()
        self.index += 1

    def append_row(self, table, row_data):
        row_idx = table.rowCount()
        table.insertRow(row_idx)
        for col_idx, val in enumerate(row_data):
            table.setItem(row_idx, col_idx, QTableWidgetItem(str(val)))
        # 스크롤을 아래로 내려서 최신 행이 보이도록 함
        table.scrollToBottom()

    def update_sensor_status_cards(self, sensor_row):
        """센서 상태 카드 업데이트"""
        for sensor, card in self.sensor_status_cards.items():
            if sensor not in sensor_row:
                continue
                
            value = sensor_row[sensor]
            threshold_info = self.sensor_thresholds[sensor]
            icon = threshold_info["icon"]
            name = threshold_info["name"]
            unit = threshold_info["unit"]
            threshold = threshold_info["threshold"]
            operator = threshold_info["operator"]
            
            # 기준치 초과 여부 확인
            exceeded = False
            if operator == ">=":
                exceeded = value >= threshold
            elif operator == "<=":
                exceeded = value <= threshold
                
            # 카드 텍스트 설정
            status_text = f"{icon} {name}: {value}{unit}"
            if exceeded:
                status_text += f" 🔺 기준 초과"
                card.setStyleSheet("""
                    QLabel {
                        background-color: #ffebee;
                        border: 2px solid #e53935;
                        border-radius: 5px;
                        padding: 10px;
                        font-size: 14px;
                        font-weight: bold;
                        color: #d32f2f;
                    }
                """)
            else:
                card.setStyleSheet("""
                    QLabel {
                        background-color: #e8f5e9;
                        border: 1px solid #4caf50;
                        border-radius: 5px;
                        padding: 10px;
                        font-size: 14px;
                        color: #2e7d32;
                    }
                """)
                
            card.setText(status_text)

    def update_sensor_graphs(self, df):
        """모든 센서 그래프 업데이트"""
        sensor_names = ["temperature", "humidity", "co2", "vibration"]
        
        for sensor in sensor_names:
            if sensor in df.columns:
                figure_dict = self.sensor_tab["figures"][sensor]
                figure = figure_dict["figure"]
                figure.clear()
                
                # 여백 설정 (그래프 그리기 전에 설정)
                figure.subplots_adjust(bottom=0.25, top=0.9, left=0.1, right=0.9)
                
                ax = figure.add_subplot(111)
                ax.plot(pd.to_datetime(df["timestamp"]), df[sensor], label=sensor, color="#e53935")
                
                # 임계선 추가
                threshold = self.sensor_thresholds[sensor]["threshold"]
                operator = self.sensor_thresholds[sensor]["operator"]
                
                if operator == ">=":
                    ax.axhline(y=threshold, color='r', linestyle='--', alpha=0.5, label=f"임계값: {threshold}")
                elif operator == "<=":
                    ax.axhline(y=threshold, color='r', linestyle='--', alpha=0.5, label=f"임계값: {threshold}")
                
                # 그래프 스타일 설정
                title_text = f"{self.sensor_thresholds[sensor]['icon']} {self.sensor_thresholds[sensor]['name']} 실시간 추이"
                ax.set_title(title_text, fontsize=11)
                ax.set_xlabel("시간", labelpad=8, fontsize=10)
                ax.set_ylabel(f"{self.sensor_thresholds[sensor]['name']} ({self.sensor_thresholds[sensor]['unit']})", labelpad=8, fontsize=10)
                ax.tick_params(axis='x', rotation=30, labelsize=8)
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.legend(loc='upper right', fontsize=9)
                
                # 타이트 레이아웃 적용
                figure.tight_layout()
                # 그래프 갱신
                figure_dict["canvas"].draw()

    def update_plot(self, fig, df, x_col, y_col):
        fig.clear()
        
        # 여백 설정 (그래프 그리기 전에 설정)
        fig.subplots_adjust(bottom=0.2, top=0.9, left=0.12, right=0.9)
        
        ax = fig.add_subplot(111)
        ax.plot(pd.to_datetime(df[x_col]), df[y_col], label=y_col)
        ax.set_title(f"{y_col} 실시간 추이", fontsize=11)
        ax.set_xlabel("시간", labelpad=8, fontsize=10)
        ax.tick_params(axis='x', rotation=30, labelsize=8)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper right', fontsize=9)
        fig.tight_layout()
        fig.canvas.draw()
    
    ###
    # 예측 통계 요약 탭 생성 함수
    def create_stats_summary_tab(self):
        """예측 통계 요약 탭 생성"""
        tab_widget = QWidget()
        layout = QVBoxLayout()
        tab_widget.setLayout(layout)
        
        # 설명 라벨 추가
        title_label = QLabel("실시간 예측 통계 요약")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
            padding: 5px;
            color: #333;
        """)
        layout.addWidget(title_label)
        
        # 파이 차트를 위한 컨테이너 생성
        charts_container = QWidget()
        charts_layout = QGridLayout()
        charts_container.setLayout(charts_layout)
        
        # 위험 예측 파이 차트
        risk_figure = Figure(figsize=(5, 4), dpi=100)
        risk_canvas = FigureCanvas(risk_figure)
        risk_canvas.setMinimumHeight(300)
        
        # 위험 예측 영역에 제목과 차트 추가
        risk_frame = QFrame()
        risk_frame.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border-radius: 8px;
                border: 1px solid #ddd;
                padding: 10px;
                margin: 5px;
            }
        """)
        risk_layout = QVBoxLayout(risk_frame)
        risk_title = QLabel("위험 예측 분포")
        risk_title.setAlignment(Qt.AlignCenter)
        risk_title.setStyleSheet("font-weight: bold; color: #e53935;")
        risk_layout.addWidget(risk_title)
        risk_layout.addWidget(risk_canvas)
        
        # 다른 예측 차트를 위한 자리 확보 (확장성)
        charts_layout.addWidget(risk_frame, 0, 0)
        
        # 통계 정보 테이블
        stats_table = QTableWidget(3, 2)  # 3행(safe, risk, warning), 2열(카테고리, 개수)
        stats_table.setHorizontalHeaderLabels(["카테고리", "개수"])
        stats_table.verticalHeader().setVisible(False)
        stats_table.setItem(0, 0, QTableWidgetItem("Safe"))
        stats_table.setItem(1, 0, QTableWidgetItem("Risk"))
        stats_table.setItem(2, 0, QTableWidgetItem("Warning"))
        
        # 테이블 스타일 설정
        stats_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ccc;
                border: 1px solid #ddd;
            }
            QHeaderView::section {
                background-color: #e53935;
                color: white;
                padding: 6px;
                font-weight: bold;
            }
        """)
        stats_table.setMaximumHeight(150)
        
        # 카테고리 셀 색상 설정
        safe_item = stats_table.item(0, 0)
        safe_item.setBackground(Qt.green)
        risk_item = stats_table.item(1, 0)
        risk_item.setBackground(Qt.red)
        warning_item = stats_table.item(2, 0)
        warning_item.setBackground(Qt.yellow)
        
        # 테이블 셀 정렬
        for row in range(3):
            stats_table.setItem(row, 1, QTableWidgetItem("0"))
            for col in range(2):
                item = stats_table.item(row, col)
                item.setTextAlignment(Qt.AlignCenter)
        
        # 테이블 헤더 설정
        header = stats_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        # 레이아웃에 추가
        layout.addWidget(charts_container)
        layout.addWidget(stats_table)
        
        return {
            "widget": tab_widget,
            "risk_figure": risk_figure,
            "risk_canvas": risk_canvas,
            "stats_table": stats_table
        }

    # 파이 차트 업데이트 함수
    def update_prediction_stats(self):
        """예측 통계 요약 업데이트"""
        # 탭이 없으면 업데이트하지 않음
        if "예측 통계 요약" not in self.stats_tabs:
            return
        
        stats_tab = self.stats_tabs["예측 통계 요약"]
        
        # 위험 예측 데이터 집계
        if "위험 예측" in self.predictions and not self.predictions["위험 예측"].empty:
            risk_df = self.predictions["위험 예측"]
            
            # 현재까지 표시된 데이터만 집계 (self.index까지)
            if self.index <= len(risk_df):
                current_data = risk_df.iloc[:self.index]
                
                # risk_prediction 컬럼 값 집계
                if "risk_prediction" in current_data.columns:
                    value_counts = current_data["risk_prediction"].value_counts()
                    
                    # 파이 차트 업데이트
                    fig = stats_tab["risk_figure"]
                    fig.clear()
                    fig.patch.set_facecolor('#f8f9fa')
                    ax = fig.add_subplot(111)
                    
                    # 데이터가 있는 경우만 파이 차트 그리기
                    if not value_counts.empty:
                        # 색상 매핑
                        colors = {'safe': '#4caf50', 'risk': '#f44336', 'warning': '#ffeb3b'}
                        chart_colors = [colors.get(val, '#9e9e9e') for val in value_counts.index]
                        
                        # 파이 차트 그리기
                        wedges, texts, autotexts = ax.pie(
                            value_counts, 
                            labels=value_counts.index,
                            autopct='%1.1f%%',
                            pctdistance=0.75,
                            startangle=90,
                            colors=chart_colors,
                            shadow=True,
                            explode=[0.05 if val == 'risk' else 0 for val in value_counts.index],  # 위험 카테고리를 살짝 돌출
                            wedgeprops={'edgecolor': 'white', 'linewidth': 1}
                            
                        )
                        
                        # 텍스트 스타일 설정
                        for text in texts:
                            text.set_fontsize(11)
                            text.set_fontweight('bold')
                        for autotext in autotexts:
                            autotext.set_fontsize(10)
                            autotext.set_color('white')
                            autotext.set_fontweight('bold')
                        
                        ax.set_title('위험 예측 분포', fontsize=14, fontweight='bold', color='#e53935')
                        ax.axis('equal')  # 원형 유지

                        # 범례 추가
                        legend = ax.legend(
                            wedges, 
                            [f"{idx}: {val} 건" for idx, val in zip(value_counts.index, value_counts.values)],
                            title="예측 분류",
                            loc="center left",
                            bbox_to_anchor=(1, 0, 0.5, 1),
                            frameon=True,
                            framealpha=0.9,
                            edgecolor='#dddddd'
                        )
                        legend.get_title().set_fontweight('bold')
                        
                        # 통계 테이블 업데이트
                        stats_table = stats_tab["stats_table"]
                        
                        # 기본값 0으로 설정
                        for row, category in enumerate(['safe', 'risk', 'warning']):
                            count = value_counts.get(category, 0)
                            count_item = QTableWidgetItem(str(count))
                            count_item.setTextAlignment(Qt.AlignCenter)

                            if count > 0:
                                count_item.setFont(QFont("Arial", 10, QFont.Bold))
                        
                            stats_table.setItem(row, 1, count_item)
                    else:
                        # 데이터가 없는 경우 안내 메시지 표시
                        ax.set_facecolor('#f5f5f5')
                        ax.text(0.5, 0.5, '데이터 수집 중...', 
                                horizontalalignment='center',
                                verticalalignment='center',
                                fontsize=14,
                                fontweight='bold',
                                color='#757575')
                    
                    # 캔버스 업데이트
                    fig.tight_layout()
                    stats_tab["risk_canvas"].draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = RealtimePredictDashboard()
    dashboard.show()
    sys.exit(app.exec_())