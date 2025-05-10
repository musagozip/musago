import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime
import matplotlib.font_manager as fm
import os

report_timestamp = datetime.now().strftime("%Y.%m.%d %p %I:%M")
filename_timestamp = datetime.now().strftime("%Y%m%d_%H%M")

# ---------- 🔹 한글 폰트 설정 (Windows용) ----------
font_path = "C:/Windows/Fonts/malgun.ttf"  # 윈도우 기본 맑은 고딕
font_name = fm.FontProperties(fname=font_path).get_name()
plt.rcParams['font.family'] = font_name

# ---------- Step 1. 데이터 불러오기 ----------
df = pd.read_csv("shared/data/sensor_result.csv")  
df['timestamp'] = pd.to_datetime(df['timestamp'])
report_date = df['timestamp'].max().date()

# ---------- Step 2. 통계 요약 ----------
total_records = len(df)
red_warnings = (df[['temp_status', 'hum_status', 'co2_status', 'vib_status', 'energy_status']] == 'red').sum().sum()

# 평균/최댓값 계산
sensor_metrics = {
    '온도': ('temperature', '℃'),
    '습도': ('humidity', '%'),
    'CO2': ('co2', 'ppm'),
    '진동': ('vibration', 'mm/s'),
    '전력': ('energy_usage', 'W')
}
sensor_summary = []
for label, (col, unit) in sensor_metrics.items():
    avg = df[col].mean()
    max_val = df[col].max()
    sensor_summary.append(f"· {label} → 평균: {avg:.1f}{unit} / 최대: {max_val:.1f}{unit}")

# ---------- ✅ 상태별 분포 요약표 만들기 ----------
status_cols = ['temp_status', 'hum_status', 'co2_status', 'vib_status', 'energy_status']
status_labels = ['온도 센서', '습도 센서', 'CO2 센서', '진동 센서', '에너지 센서']
status_summary = []

for col, label in zip(status_cols, status_labels):
    counts = df[col].value_counts().to_dict()
    summary_str = f"· {label}: " + ", ".join([f"{k}={v}" for k, v in counts.items()])
    status_summary.append(summary_str)

# ---------- Step 3-1. 센서별 추이 그래프 저장  ----------
sensor_cols = ['temperature', 'humidity', 'co2', 'vibration']
sensor_labels = ['온도', '습도', 'CO2', '진동']
trend_images = []

# 센서별 경고 기준선
thresholds = {
    'temperature': 30,
    'humidity': 70,
    'co2': 1000,
    'vibration': 8
}

for col, label in zip(sensor_cols, sensor_labels):
    fig, ax1 = plt.subplots(figsize=(10, 4))

    # 좌측 y축: 에너지
    color1 = 'deepskyblue'
    ax1.set_xlabel("시간")
    ax1.set_ylabel("전력 사용량", color=color1)
    ax1.plot(df['timestamp'], df['energy_usage'], label='에너지', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, axis='y', linestyle='--', linewidth=0.5)

    # 우측 y축: 센서 값
    ax2 = ax1.twinx()
    color2 = {'temperature': 'purple', 'humidity': 'orange', 'co2': 'blue', 'vibration': 'green'}[col]
    ax2.set_ylabel(label, color=color2)
    ax2.plot(df['timestamp'], df[col], label=label, color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.grid(True, axis='y', linestyle='--', linewidth=0.5)

    # 빨간 경고 기준선
    if col in thresholds:
        ax2.axhline(y=thresholds[col], color='red', linestyle='--', linewidth=2)

    plt.title(f"{label} vs 전력 사용량")
    plt.xticks(rotation=45)
    plt.tight_layout()

    img_name = f"{col}_trend.png"
    plt.savefig(img_name)
    plt.close()
    trend_images.append((label, img_name))



# ---------- Step 3-2. 센서 상태 파이차트 저장 ----------
pie_images = []
ordered_labels = ['green', 'yellow', 'red']
status_colors = ['#2ca02c', '#ffcc00', '#ff0000']  # 초록, 노랑, 빨강

for col, label in zip(status_cols, status_labels):
    counts = df[col].value_counts()

    # 모든 상태가 다 있을 수도 있고, 일부만 있을 수도 있으니 0 채워주기
    counts = {key: counts.get(key, 0) for key in ordered_labels}
    values = [counts[label] for label in ordered_labels]

    # 차트 저장
    plt.figure(figsize=(5, 5))
    plt.pie(
        values,
        labels=ordered_labels,
        colors=status_colors,
        autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
        startangle=140,
        textprops={'fontsize': 17}
    )
    plt.tight_layout()
    img_name = f"{col}_pie.png"
    plt.savefig(img_name)
    plt.close()

    pie_images.append((label, img_name))


# ---------- Step 4. PDF 작성 ----------
pdf = FPDF()
pdf.add_page()
pdf.add_font('Malgun', '', font_path, uni=True)
pdf.set_font('Malgun', '', 13)

pdf.set_font("Malgun", size=25)
pdf.cell(w=0, h=10, txt="스마트 산업현장 일일 위험 리포트", ln=True, align="C")

pdf.ln(7)
pdf.set_font("Malgun", size=11)
pdf.cell(w=0, h=10, txt=f"리포트 생성 시각 : {report_timestamp}", ln=True, align="R")


# ---------- ✅ 센서 상태별 분포도  ----------
pdf.ln(10)
pdf.set_font("Malgun", size=15)
pdf.cell(200, 10, txt="[ 센서별 상태 분석 ]", ln=True)

for (status_col, label), (label2, image_path) in zip(zip(status_cols, status_labels), pie_images):
    sensor_eng_name = status_col.split('_')[0]

    # 상태 분포
    counts = df[status_col].value_counts().to_dict()
    status_summary = ", ".join([f"{k}={v}" for k, v in counts.items()])

    # 평균/최대값
    avg_max_line = ""
    for name, (col, unit) in sensor_metrics.items():
        if col.startswith(sensor_eng_name):
            avg = df[col].mean()
            max_val = df[col].max()
            avg_max_line_1 = f"     - 평균 : {avg:.1f}{unit}"
            avg_max_line_2 = f"       최대 : {max_val:.1f}{unit}"

            break

    # 줄1: 센서명
    pdf.ln(2)
    pdf.set_font("Malgun", size=12)  # 👈 글씨 작게
    pdf.cell(120, 8, txt=f"· {label}", ln=True)
    pdf.set_font("Malgun", size=11)  # 👈 다시 기본 크기 복귀

    # 줄2: 상태별 개수
    pdf.ln(7)
    pdf.set_font("Malgun", size=11)  # 👈 글씨 작게
    pdf.cell(120, 8, txt=f"     - {status_summary}", ln=True)
    pdf.set_font("Malgun", size=11)  # 👈 다시 기본 크기 복귀

    # 줄3: 평균/최대 + 파이차트
    pdf.ln(5)
    y_current = pdf.get_y()
    pdf.set_font("Malgun", size=11)  # 👈 글씨 작게
    pdf.cell(120, 8, txt=avg_max_line_1, ln=True)
    pdf.cell(120, 8, txt=avg_max_line_2, ln=False)
    pdf.set_font("Malgun", size=11)  # 👈 다시 기본 크기 복귀
    pdf.image(image_path, x=130, y=y_current - 25, w=55, h=55)
    pdf.ln(40)


# ---------- 센서별 추이 그래프 ----------
pdf.ln(15)
pdf.set_font("Malgun", size=15)
pdf.cell(200, 10, txt="[ 센서별 추이 그래프 ]", ln=True)
pdf.ln(2)
for label, image_path in trend_images:
    pdf.set_font("Malgun", size=12)
    pdf.cell(200, 10, txt=f"· {label} vs 전력 사용량", ln=True)
    pdf.image(image_path, x=10, y=None, w=180)
    pdf.ln(10)

# ---------- ✅ 위험도 우선순위 분석 ----------
pdf.ln(15)
pdf.set_font("Malgun", size=15)
pdf.cell(200, 10, txt="[ 위험 센서 우선순위 (Red 경고 기준) ]", ln=True)
pdf.set_font("Malgun", size=12)

red_counts = []
for col, label in zip(status_cols, status_labels):
    red_count = (df[col] == 'red').sum()
    red_counts.append((label, red_count))

# 개수 내림차순 정렬
sorted_red = sorted(red_counts, key=lambda x: x[1], reverse=True)

# 출력
pdf.ln(2)
for idx, (label, count) in enumerate(sorted_red, start=1):
    if count > 0:
        pdf.cell(200, 10, txt=f" {idx}. {label} : {count} 건", ln=True)


# ---------- 권장 조치 ----------
pdf.ln(15)
pdf.set_font("Malgun", size=15)
pdf.cell(200, 10, txt="[ 권장 조치 ]", ln=True)
pdf.set_font("Malgun", size=12)

line_height = 8  # 줄 높이

# 온도 (기준: 30 초과 red / 27 초과 yellow / 나머지 green)
temp_max = df['temperature'].max()
if temp_max > 30:
    pdf.cell(200, line_height, txt="· 고온 감지됨 (30°C 초과)", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 내부 환기 또는 냉방 설비 가동 필요", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 장비 가동 시간 분산 및 고열 장비 점검 필요", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 고온 지역 작업 시 보호구 착용 권장", ln=True)
    pdf.ln(4)
elif temp_max > 27:
    pdf.cell(200, line_height, txt="· 온도 상승 주의 (27°C 초과)", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 냉방 설비 사전 점검 권장", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 작업 환경 온도 모니터링 지속 필요", ln=True)
    pdf.ln(4)

# 습도 (기준: 35 미만 red / 45 미만 yellow / 이상 green)
hum_min = df['humidity'].min()
if hum_min < 35:
    pdf.cell(200, line_height, txt="· 저습 감지됨 (35% 미만)", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 가습기 가동 및 습도 조절 필요", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 정전기 발생 주의", ln=True)
    pdf.ln(4)
elif hum_min < 45:
    pdf.cell(200, line_height, txt="· 습도 낮음 주의 (45% 미만)", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 습도 유지 장치 점검 권장", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 민감 장비 습도 관리 필요", ln=True)
    pdf.ln(4)

# CO2 (기준: 1000 초과 red / 700 초과 yellow / 이하 green)
co2_max = df['co2'].max()
if co2_max > 1000:
    pdf.cell(200, line_height, txt="· CO₂ 농도 과다 (1000ppm 초과)", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 환기 시스템 즉시 가동", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 밀폐 공간 내 작업자 체류 시간 제한 필요", ln=True)
    pdf.ln(4)
elif co2_max > 700:
    pdf.cell(200, line_height, txt="· CO₂ 농도 상승 주의 (700ppm 초과)", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 주기적 환기 권장", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> co2 센서 및 환기 필터 점검 권장", ln=True)
    pdf.ln(4)

# 진동 (기준: 8 초과 red / 5 초과 yellow / 이하 green)
vib_max = df['vibration'].max()
if vib_max > 8:
    pdf.cell(200, line_height, txt="· 과도한 진동 감지됨 (8 초과)", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 즉시 장비 운전 중단 및 정밀 점검 필요", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 구조물 안정성 및 고장 가능성 확인", ln=True)
    pdf.ln(4)
elif vib_max > 5:
    pdf.cell(200, line_height, txt="· 진동 증가 주의 (5 초과)", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 장비 상태 모니터링 강화 필요", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 이상 진동 발생 장비 선별 점검", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 지속 진동 시 운전 중단 및 정밀 진단 필요", ln=True)
    pdf.ln(4)

# 에너지
if df['energy_usage'].max() > 1000:
    pdf.cell(200, line_height, txt="· 에너지 과소비 감지 (1000W 초과)", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 일부 기기 절전모드 또는 중단 필요", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 피크 시간대 에너지 부하 분산 권장", ln=True)
    pdf.ln(4)

elif df['energy_usage'].max() > 800:
    pdf.cell(200, line_height, txt="· 에너지 사용량 주의 (800W 초과)", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 사용량 점검 필요", ln=True)
    pdf.set_x(20)
    pdf.cell(200, line_height, txt="--> 불필요 설비 일시 정지 고려", ln=True)
    pdf.ln(4)


# ---------- Step 5. 저장 ----------
# 🔹 현재 날짜+시간 가져오기
now = datetime.now()

# 🔹 PDF 내부에 표시될 시각 형식: "2025.05.01 PM 03:30"
report_timestamp = now.strftime("%Y.%m.%d %p %I:%M")

# 🔹 파일 저장용 시각 형식: "20250501_1530"
filename_timestamp = now.strftime("%Y%m%d_%H%M")

# 🔹 저장 파일명에 반영
output_filename = f"daily_report_{filename_timestamp}.pdf"
output_path = os.path.join(os.getcwd(), output_filename)

pdf.output(output_path)
print(f"📄 PDF 리포트 생성 완료: {output_path}")