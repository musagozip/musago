import pandas as pd
import joblib

df = pd.read_csv("shared/data/sensor_result.csv")
model = joblib.load("python/models/energy_model.pkl")
X = df[["temperature", "humidity", "co2", "vibration", "energy_usage"]]
df["energy_prediction"] = model.predict(X)
df.to_csv("shared/data/energy_prediction.csv", index=False, encoding="utf-8-sig")
print("✅ energy_prediction.csv 저장 완료!")
