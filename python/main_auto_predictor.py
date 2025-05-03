import os
import time

INTERVAL = 10  # 반복 주기 (초)

print("🚀 통합 예측 자동화 시스템 시작 (Ctrl+C로 종료)")

while True:
    print("\n📅 현재 시간:", time.strftime("%Y-%m-%d %H:%M:%S"))

    # 1️⃣ C++ 센서 시뮬레이터 실행
    print("📡 센서 데이터 생성 중...")
    os.chdir("cpp/sensor_simulator/x64/Debug")  # .exe가 있는 폴더로 이동
    os.system("sensor_simulator.exe")           # 시뮬레이터 실행
    time.sleep(0.5)                             # 생성 대기
    os.chdir("../../../..")                     # 루트 디렉토리로 복귀

    # 2️⃣ 위험 예측 + 저장
    print("🧠 위험 예측 중...")
    os.system("python python/predict_risk.py")
    os.system("python python/save_risk_to_db.py")

    # 3️⃣ 고장 예측 + 저장
    print("🛠 고장 예측 중...")
    os.system("python python/predict_fault.py")
    os.system("python python/save_fault_to_db.py")

    # 4️⃣ 복합 위험 등급 예측 + 저장
    print("📊 위험 등급 예측 중...")
    os.system("python python/predict_risk_level.py")
    os.system("python python/save_risk_level_to_db.py")

    # 5️⃣ 이상치 탐지 + 저장
    print("🚨 이상치 탐지 중...")
    os.system("python python/predict_anomaly.py")
    os.system("python python/save_anomaly_to_db.py")

    # 6️⃣ 에너지 예측 + 저장
    print("⚡ 에너지 예측 중...")
    os.system("python python/predict_energy.py")
    os.system("python python/save_energy_to_db.py")

    # 7️⃣ 센서 이상 감지 + 저장
    print("💥 센서 이상 감지 중...")
    os.system("python python/sensor_error_checker.py")

    # 8️⃣ CSV 백업
    print("💾 CSV 백업 중...")
    os.system("python python/backup_to_csv.py")

    print("✅ 모든 예측 완료. 다음 주기까지 대기 중...\n")
    time.sleep(INTERVAL)
