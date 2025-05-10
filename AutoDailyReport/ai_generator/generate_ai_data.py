import pandas as pd
import os

# 🔹 CSV 파일 경로 (최신 센서 시뮬레이션 결과)
input_path = "cpp/sensor_simulator/shared/data/sensor_result.csv"
# output_path = "cpp/sensor_simulator/shared/data/ai_dataset.csv"
output_path = "shared/data/ai_dataset.csv"


# 🔹 데이터 불러오기
try:
    df = pd.read_csv(input_path)
except FileNotFoundError:
    print(f"❌ 파일을 찾을 수 없습니다: {input_path}")
    exit()

# 🔹 라벨 정의 함수
def assign_label(row):
    statuses = [row["temp_status"], row["hum_status"], row["co2_status"], row["vib_status"], row["energy_status"]]
    if "red" in statuses:
        return "risk"
    elif all(s == "green" for s in statuses):
        return "safe"
    else:
        return "warning"

# 🔹 라벨 부여
df["label"] = df.apply(assign_label, axis=1)

# 🔹 필요한 컬럼만 저장
output_df = df[["temperature", "humidity", "co2", "vibration", "energy_usage", "label"]]

# 🔹 저장 디렉토리 확인 및 저장
os.makedirs(os.path.dirname(output_path), exist_ok=True)
output_df.to_csv(output_path, index=False, encoding="utf-8-sig")

print(f"✅ AI 학습용 데이터셋 저장 완료: {output_path}")
