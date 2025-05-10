import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# 🔹 모델 저장 폴더 생성
os.makedirs("python/models", exist_ok=True)

# 🔹 데이터 불러오기
df = pd.read_csv("shared/data/ai_dataset.csv")

# 🔹 에너지 상태 기반 데이터 구성
df["energy_label"] = df["energy_usage"].apply(lambda x: "overuse" if x > 1000 else "normal")

X = df[["temperature", "humidity", "co2", "vibration", "energy_usage"]]
y = df["energy_label"]

# 🔹 학습/검증 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔹 모델 학습
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 🔹 모델 저장
joblib.dump(model, "python/models/energy_model.pkl")
print("✅ energy_model.pkl 저장 완료!")
