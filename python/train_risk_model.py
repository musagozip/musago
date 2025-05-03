import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os

# 🔹 모델 저장 폴더 생성
os.makedirs("python/models", exist_ok=True)

# 🔹 데이터 불러오기
df = pd.read_csv("shared/data/ai_dataset.csv")

# 🔹 입력(X), 출력(y) 분리
X = df[["temperature", "humidity", "co2", "vibration", "energy_usage"]]
y = df["label"]

# 🔹 학습/검증 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔹 랜덤포레스트 모델 학습
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 🔹 평가 출력
y_pred = model.predict(X_test)
print("✅ 분류 성능:\n")
print(classification_report(y_test, y_pred))

# 🔹 모델 저장
joblib.dump(model, "python/models/risk_model.pkl")
print("✅ 모델 저장 완료: python/models/risk_model.pkl")
