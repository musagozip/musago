import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

# 🔹 모델 저장 폴더 생성
os.makedirs("python/models", exist_ok=True)

# 🔹 데이터 불러오기
df = pd.read_csv("shared/data/ai_dataset.csv")

# 🔹 고장(fault) 예측용 라벨 만들기
df["fault_label"] = df["vibration"].apply(lambda x: "fault" if x > 8.0 else "normal")

X = df[["vibration"]]
y = df["fault_label"]

# 🔹 학습/검증 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🔹 모델 학습
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 🔹 모델 저장
joblib.dump(model, "python/models/fault_model.pkl")
print("✅ fault_model.pkl 저장 완료!")
