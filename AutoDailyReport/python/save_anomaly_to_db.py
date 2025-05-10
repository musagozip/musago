import pandas as pd
import mysql.connector

df = pd.read_csv("shared/data/anomaly_prediction.csv")
filtered_df = df[df["anomaly_prediction"] == -1].copy()  # -1이면 이상치

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="musago_db"
)
cursor = conn.cursor()

for _, row in filtered_df.iterrows():
    cursor.execute("""
        INSERT INTO anomaly_log (timestamp, temperature, humidity, co2, vibration, energy_usage)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        row["timestamp"], row["temperature"], row["humidity"],
        row["co2"], row["vibration"], row["energy_usage"]
    ))

conn.commit()
cursor.close()
conn.close()

print(f"✅ {len(filtered_df)}건의 이상치 데이터를 anomaly_log 테이블에 저장 완료!")
