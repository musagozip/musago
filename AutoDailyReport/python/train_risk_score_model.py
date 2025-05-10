import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

# 🔹 모델 저장 폴더 생성
os.makedirs("python/models", exist_ok=True)

# 🔹 데이터 불러오기
df = pd.read_csv("shared/data/ai_dataset.csv")

# 🔹 위험 점수 계산 함수 (센서 수치 기반 직접 계산)
def calculate_score(row):
    score = 0

    # 온도 기준
    if row["temperature"] > 30:
        score += 3
    elif row["temperature"] > 27:
        score += 1

    # 습도 기준
    if row["humidity"] < 35:
        score += 3
    elif row["humidity"] < 45:
        score += 1

    # CO2 기준
    if row["co2"] > 1000:
        score += 3
    elif row["co2"] > 700:
        score += 1

    # 진동 기준
    if row["vibration"] > 8.0:
        score += 3
    elif row["vibration"] > 5.0:
        score += 1

    # 에너지 기준
    if row["energy_usage"] > 1000:
        score += 3
    elif row["energy_usage"] > 800:
        score += 1

    return score

# 🔹 위험 점수 생성
df["risk_score"] = df.apply(calculate_score, axis=1)

X = df[["temperature", "humidity", "co2", "vibration", "energy_usage"]]
y = df["risk_score"]

# 🔹 회귀 모델 학습
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X, y)

# 🔹 모델 저장
joblib.dump(model, "python/models/risk_score_model.pkl")
print("✅ risk_score_model.pkl 저장 완료!")
