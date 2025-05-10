import pandas as pd
import joblib

# 데이터 로드
df = pd.read_csv("shared/data/sensor_result.csv")

# 모델 로드
model = joblib.load("python/models/risk_model.pkl")

# 예측
X = df[["temperature", "humidity", "co2", "vibration", "energy_usage"]]
df["risk_prediction"] = model.predict(X)

# 저장
df.to_csv("shared/data/risk_prediction.csv", index=False, encoding="utf-8-sig")
print("✅ 위험 예측 완료: shared/data/risk_prediction.csv")
