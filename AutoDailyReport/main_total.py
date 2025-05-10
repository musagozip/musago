# main_total.py

import subprocess
import time
import os

def run_step(description, command, shell=False):
    print(f"\n▶ {description} 중...")
    try:
        result = subprocess.run(command, check=True, shell=shell)
    except subprocess.CalledProcessError:
        print(f"❌ {description} 실패!")
        exit()
    print(f"✅ {description} 완료.")

# 1️⃣ 센서 시뮬레이터 실행 (.exe)
run_step("센서 시뮬레이터 실행", ["cpp/sensor_simulator/x64/Debug/sensor_simulator.exe"])

# 2️⃣ AI 예측 (단 1회 실행)
run_step("AI 예측 수행", ["python", "python/single_run_predictor.py"])

# 3️⃣ 리포트 생성
run_step("PDF 리포트 생성", ["python", "report_generator.py"])

print("\n🎉 모든 작업 완료! PDF 리포트를 확인하세요.")
