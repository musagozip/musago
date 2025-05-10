import pandas as pd
import mysql.connector

df = pd.read_csv("shared/data/fault_prediction.csv")
filtered_df = df[df["fault_prediction"] == "fault"].copy()

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="musago_db"
)
cursor = conn.cursor()

for _, row in filtered_df.iterrows():
    cursor.execute("""
        INSERT INTO fault_log (timestamp, vibration, fault_prediction)
        VALUES (%s, %s, %s)
    """, (
        row["timestamp"], row["vibration"], row["fault_prediction"]
    ))

conn.commit()
cursor.close()
conn.close()

print(f"✅ {len(filtered_df)}건의 고장 데이터를 fault_log 테이블에 저장 완료!")
