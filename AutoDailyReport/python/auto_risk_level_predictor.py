import time
import os

# 🔁 반복 주기 설정 (초)
INTERVAL = 10  # 10초마다 예측 반복

print("🔄 복합 위험 등급 예측 자동화 시작... (Ctrl+C로 종료)")

while True:
    print("\n[복합 위험 예측] 현재 시간:", time.strftime("%Y-%m-%d %H:%M:%S"))

    # 🔹 예측 수행
    os.system("python python/predict_risk_level.py")

    # 🔹 DB 저장
    os.system("python python/save_risk_level_to_db.py")

    print("[예측 완료] 대기 중...\n")
    time.sleep(INTERVAL)
