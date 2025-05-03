import pandas as pd
import joblib

df = pd.read_csv("shared/data/sensor_result.csv")
model = joblib.load("python/models/risk_score_model.pkl")
X = df[["temperature", "humidity", "co2", "vibration", "energy_usage"]]
df["risk_score"] = model.predict(X)

predictions = model.predict(X)
df["risk_score"] = predictions.round().astype(int)  # <-- 핵심 추가!

def classify(score):
    return "High" if score >= 4 else ("Medium" if score >= 2 else "Low")

df["risk_level"] = df["risk_score"].apply(classify)
df.to_csv("shared/data/risk_level_prediction.csv", index=False, encoding="utf-8-sig")
print("✅ risk_level_prediction.csv 저장 완료!")
