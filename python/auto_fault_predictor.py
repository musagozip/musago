import time
import os

# 🔁 반복 주기 설정 (초)
INTERVAL = 10  # 10초마다 반복

print("🔄 고장 예측 자동화 시작... (Ctrl+C로 중지 가능)")

while True:
    print("\n[고장 예측 시작] 현재 시간:", time.strftime("%Y-%m-%d %H:%M:%S"))

    # 🔹 1. 고장 예측 실행
    os.system("python python/predict_fault.py")

    # 🔹 2. 고장 예측 결과 DB 저장
    os.system("python python/save_fault_to_db.py")

    print("[고장 예측 완료] 대기 중...\n")
    time.sleep(INTERVAL)
