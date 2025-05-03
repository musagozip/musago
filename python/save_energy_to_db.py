import pandas as pd
import mysql.connector

df = pd.read_csv("shared/data/energy_prediction.csv")
filtered_df = df[df["energy_prediction"] == "overuse"].copy()

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="musago_db"
)
cursor = conn.cursor()

for _, row in filtered_df.iterrows():
    cursor.execute("""
        INSERT INTO energy_log (timestamp, energy_usage, energy_prediction)
        VALUES (%s, %s, %s)
    """, (
        row["timestamp"], row["energy_usage"], row["energy_prediction"]
    ))

conn.commit()
cursor.close()
conn.close()

print(f"✅ {len(filtered_df)}건의 에너지 과소비 데이터를 energy_log 테이블에 저장 완료!")
