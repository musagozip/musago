import time
import os

INTERVAL = 10

print("🔁 에너지 예측 자동화 시작...")

while True:
    print("[에너지 예측] 현재:", time.strftime("%Y-%m-%d %H:%M:%S"))
    os.system("python python/predict_energy.py")
    os.system("python python/save_energy_to_db.py")
    print("[완료] 대기 중...\n")
    time.sleep(INTERVAL)
