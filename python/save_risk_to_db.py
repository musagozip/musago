import pandas as pd
import mysql.connector

# 🔹 데이터 로드
df = pd.read_csv("shared/data/risk_prediction.csv")

# 🔹 위험 데이터만 필터링
filtered_df = df[df["risk_prediction"] != "safe"].copy()

# 🔹 MySQL 연결
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="musago_db"
)
cursor = conn.cursor()

# 🔹 데이터 삽입
for _, row in filtered_df.iterrows():
    cursor.execute("""
        INSERT INTO event_log (timestamp, temperature, humidity, co2, vibration, energy_usage, risk_prediction)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        row["timestamp"], row["temperature"], row["humidity"], row["co2"],
        row["vibration"], row["energy_usage"], row["risk_prediction"]
    ))

conn.commit()
cursor.close()
conn.close()

print(f"✅ {len(filtered_df)}건의 위험 이벤트를 event_log 테이블에 저장 완료!")
