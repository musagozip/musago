import time
import os

# 🔁 반복 주기 (초)
INTERVAL = 10  # 10초마다 반복

print("⏳ AI 위험 예측 자동화 시작... (Ctrl+C로 종료)")

while True:
    print("\n[예측 시작] 현재 시간:", time.strftime("%Y-%m-%d %H:%M:%S"))

    # 🔹 1단계: 예측 수행
    os.system("python python/predict_risk.py")

    # 🔹 2단계: 위험 데이터 DB 저장
    os.system("python python/save_risk_to_db.py")

    print("[예측 완료] 대기 중...\n")
    time.sleep(INTERVAL)
