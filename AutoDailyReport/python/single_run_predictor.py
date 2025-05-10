# single_run_predictor.py

import os

print("\n📌 [AI 예측 시작]")

# 1️⃣ 센서 데이터 생성 (C++ 시뮬레이터가 이미 수행됨)
if not os.path.exists("shared/data/sensor_result.csv"):
    print("❌ sensor_result.csv 파일이 없습니다.")
    exit()

# 2️⃣ 위험 예측 + 저장
print("🧠 위험 예측 중...")
os.system("python python/predict_risk.py")
os.system("python python/save_risk_to_db.py")

# 3️⃣ 고장 예측 + 저장
print("🛠 고장 예측 중...")
os.system("python python/predict_fault.py")
os.system("python python/save_fault_to_db.py")

# 4️⃣ 위험 등급 예측 + 저장
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

print("✅ 모든 예측 완료")
