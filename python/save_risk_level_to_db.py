import pandas as pd
import mysql.connector

df = pd.read_csv("shared/data/risk_level_prediction.csv")

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="musago_db"
)
cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO risk_level_log (timestamp, risk_score, risk_level)
        VALUES (%s, %s, %s)
    """, (
        row["timestamp"], row["risk_score"], row["risk_level"]
    ))

conn.commit()
cursor.close()
conn.close()

print(f"✅ {len(df)}건의 위험 등급 데이터를 risk_level_log 테이블에 저장 완료!")
