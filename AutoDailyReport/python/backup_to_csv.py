import os
import pandas as pd
import mysql.connector
from datetime import datetime

# 🔹 MySQL 연결 정보
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "musago_db"
}

# 🔹 백업할 테이블 목록
tables = [
    "event_log",
    "fault_log",
    "risk_level_log",
    "anomaly_log",
    "energy_log"
]

# 🔹 저장 경로
BASE_DIR = "csv"

# 🔹 현재 시간 문자열
now_str = datetime.now().strftime("%Y-%m-%d_%H-%M")

# 🔹 MySQL 연결
conn = mysql.connector.connect(**db_config)

for table in tables:
    folder_path = os.path.join(BASE_DIR, table)
    os.makedirs(folder_path, exist_ok=True)

    # 🔸 쿼리 및 저장
    df = pd.read_sql(f"SELECT * FROM {table}", con=conn)

    # 🔸 시간별 백업 파일
    backup_path = os.path.join(folder_path, f"{now_str}.csv")
    df.to_csv(backup_path, index=False, encoding="utf-8-sig")

    # 🔸 최신 버전 파일 (덮어쓰기)
    latest_path = os.path.join(folder_path, "latest.csv")
    df.to_csv(latest_path, index=False, encoding="utf-8-sig")

    print(f"✅ {table} → {backup_path} + latest.csv")

conn.close()
