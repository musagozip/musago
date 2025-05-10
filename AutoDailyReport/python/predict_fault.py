import pandas as pd
import joblib
import os

# 🔹 경로 설정
INPUT_CSV = "shared/data/sensor_result.csv"
MODEL_PATH = "python/models/fault_model.pkl"
OUTPUT_CSV = "shared/data/fault_prediction.csv"

# 🔹 모델 로드
model = joblib.load(MODEL_PATH)

# 🔹 CSV 로드
df = pd.read_csv(INPUT_CSV)

# 🔹 입력 데이터: vibration 하나만 사용
X = df[["vibration"]]

# 🔹 예측 수행
df["fault_prediction"] = model.predict(X)

# 🔹 결과 저장
df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
print("✅ 고장 예측 완료! 결과 저장:", OUTPUT_CSV)
