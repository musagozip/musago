import os
import time

INTERVAL = 10  # 초

print("🔁 이상치 자동 탐지 시작...")

while True:
    print("[이상치 탐지] 시작:", time.strftime("%Y-%m-%d %H:%M:%S"))
    os.system("python python/predict_anomaly.py")
    os.system("python python/save_anomaly_to_db.py")
    print("[완료] 대기 중...\n")
    time.sleep(INTERVAL)
