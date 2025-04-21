import pandas as pd
import time
import os
from datetime import datetime

# 원본 에너지 효율 데이터 경로
source_path = "C:/Users/user/Desktop/산업재해데이터/에너지 효율.csv"

# 시뮬레이션 실행 중 저장할 경로 (Dashboard에서 이 파일을 참조함)
target_path = "C:/Users/user/Desktop/산업재해데이터/에너지_효율_실시간.csv"

# 기존 파일 제거 후 초기화
if os.path.exists(target_path):
    os.remove(target_path)

# 원본 불러오기
df = pd.read_csv(source_path, encoding="cp949")
df["timestamp"] = pd.to_datetime(df["timestamp"])

# 헤더만 먼저 쓰기
df.iloc[:0].to_csv(target_path, index=False, encoding="cp949")

# 실시간처럼 한 줄씩 기록
for i in range(len(df)):
    row = df.iloc[[i]]  # 한 줄 DataFrame 유지
    row.to_csv(target_path, mode='a', index=False, header=False, encoding="cp949")

    print(f"⏱ {datetime.now().strftime('%H:%M:%S')} | 저장됨: {row.iloc[0]['timestamp']} / 효율: {row.iloc[0]['efficiency(%)']}%")
    time.sleep(2)  # 2초 간격
