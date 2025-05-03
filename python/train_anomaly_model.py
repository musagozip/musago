import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

# 🔹 모델 저장 폴더 생성
os.makedirs("python/models", exist_ok=True)

# 🔹 데이터 불러오기
df = pd.read_csv("shared/data/ai_dataset.csv")

# 🔹 입력(X)만 사용 (라벨은 사용 안 함)
X = df[["temperature", "humidity", "co2", "vibration", "energy_usage"]]

# 🔹 이상치 탐지 모델 학습
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(X)

# 🔹 모델 저장
joblib.dump(model, "python/models/anomaly_model.pkl")
print("✅ anomaly_model.pkl 저장 완료!")
