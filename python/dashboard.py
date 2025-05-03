import streamlit as st
import time
import pandas as pd
import mysql.connector
from mysql.connector import Error
import datetime
import plotly.graph_objects as go

# ✅ 새로고침 주기 (초 단위)
REFRESH_INTERVAL = 10

# ✅ MySQL 연결 함수
def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="musago_db"
        )
        return conn
    except Error as e:
        st.error(f"MySQL 연결 실패: {e}")
        return None

# ✅ 쿼리 실행 함수
def fetch_data(query):
    conn = get_connection()
    if conn is None:
        return pd.DataFrame()
    try:
        return pd.read_sql(query, con=conn)
    finally:
        conn.close()

# ✅ 페이지 설정
st.set_page_config(page_title="AI 예측 대시보드", layout="wide")
st.title("📊 스마트 산업현장 AI 예측 대시보드")
st.markdown("🔁 **10초마다 자동으로 데이터가 새로 고침됩니다.**")

# ✅ 현재 시각 출력
st.markdown(f"### 🔁 마지막 새로고침 시각: `{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")

# ✅ 상단 요약 카드
col1, col2, col3, col4 = st.columns(4)

# 데이터 미리 불러오기
df_event = fetch_data("SELECT * FROM event_log ORDER BY timestamp DESC LIMIT 50")
df_fault = fetch_data("SELECT * FROM fault_log ORDER BY timestamp DESC LIMIT 50")
try:
    df_sensor_error = pd.read_csv("csv/sensor_error_log/latest.csv")
except FileNotFoundError:
    df_sensor_error = pd.DataFrame()

# 요약 카드 표시
col1.metric("🚨 위험 이벤트 수", len(df_event))
col2.metric("🛠 고장 발생 수", len(df_fault))
if not df_event.empty:
    avg_energy = round(df_event["energy_usage"].mean(), 2)
    col3.metric("⚡ 평균 에너지 사용량", f"{avg_energy}")
else:
    col3.metric("⚡ 평균 에너지 사용량", "N/A")

col4.metric("💥 센서 이상 건수", len(df_sensor_error))

# ✅ 탭 구성
tabs = st.tabs(["🚨 위험 이벤트", "🛠 고장 로그", "📊 복합 위험도", "⚠ 이상치 탐지", "⚡ 에너지 과소비", "💥 센서 이상"])

# 🔹 탭 1: event_log
with tabs[0]:
    st.subheader("🚨 event_log")
    st.dataframe(df_event)

    if not df_event.empty:
        df_event = df_event.sort_values("timestamp")

        st.markdown("#### 📈 최근 위험 예측 트렌드")

        ## 첫 번째 그래프: 온도/습도/진동
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_event["timestamp"], y=df_event["temperature"], mode='lines', name='temperature'))
        fig1.add_trace(go.Scatter(x=df_event["timestamp"], y=df_event["humidity"], mode='lines', name='humidity'))
        fig1.add_trace(go.Scatter(x=df_event["timestamp"], y=df_event["vibration"], mode='lines', name='vibration'))
        fig1.update_layout(
            title="🌡 온도 / 💧 습도 / 📳 진동 트렌드",
            xaxis_title="시간",
            yaxis_title="센서 값",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=400
        )
        st.plotly_chart(fig1, use_container_width=True)

        ## 두 번째 그래프: CO₂/에너지 사용량
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_event["timestamp"], y=df_event["co2"], mode='lines', name='co2'))
        fig2.add_trace(go.Scatter(x=df_event["timestamp"], y=df_event["energy_usage"], mode='lines', name='energy_usage'))
        fig2.update_layout(
            title="🌀 CO₂ / ⚡ 에너지 사용량 트렌드",
            xaxis_title="시간",
            yaxis_title="센서 값",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            height=400
        )
        st.plotly_chart(fig2, use_container_width=True)


        st.markdown("#### ⚡ 에너지 사용량 vs 센서별 비교 (이중 Y축)")
        sub_tabs = st.tabs(["🌡 온도", "💧 습도", "📳 진동", "🌀 CO₂"])

        def plot_energy_vs(sensor_col, color, title, danger_threshold):
            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=df_event["timestamp"], y=df_event["energy_usage"],
                name="energy_usage", yaxis="y1", line=dict(color="deepskyblue")
            ))

            fig.add_trace(go.Scatter(
                x=df_event["timestamp"], y=df_event[sensor_col],
                name=sensor_col, yaxis="y2", line=dict(color=color)
            ))

            fig.add_shape(
                type="line",
                x0=df_event["timestamp"].min(), x1=df_event["timestamp"].max(),
                y0=danger_threshold, y1=danger_threshold,
                yref="y2", line=dict(color="red", width=2, dash="dash")
            )

            fig.update_layout(
                title=title,
                xaxis=dict(title="시간"),
                yaxis=dict(title="에너지 사용량", side="left"),
                yaxis2=dict(title=sensor_col, overlaying="y", side="right"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=400
            )
            return fig

        with sub_tabs[0]:  # 온도
            st.plotly_chart(plot_energy_vs("temperature", "purple", "에너지 vs 온도", danger_threshold=30), use_container_width=True)
        with sub_tabs[1]:  # 습도
            st.plotly_chart(plot_energy_vs("humidity", "orange", "에너지 vs 습도", danger_threshold=35), use_container_width=True)
        with sub_tabs[2]:  # 진동
            st.plotly_chart(plot_energy_vs("vibration", "green", "에너지 vs 진동", danger_threshold=8.0), use_container_width=True)
        with sub_tabs[3]:  # CO2
            st.plotly_chart(plot_energy_vs("co2", "blue", "에너지 vs CO₂", danger_threshold=1000), use_container_width=True)

# 🔹 탭 2: fault_log
with tabs[1]:
    st.subheader("🛠 fault_log")
    st.dataframe(fetch_data("SELECT * FROM fault_log ORDER BY timestamp DESC LIMIT 50"))

# 🔹 탭 3: risk_level_log
with tabs[2]:
    st.subheader("📊 risk_level_log")
    df_risk_level = fetch_data("SELECT * FROM risk_level_log ORDER BY timestamp DESC LIMIT 50")
    st.dataframe(df_risk_level)

    if not df_risk_level.empty:
        df_risk_level = df_risk_level.sort_values("timestamp")

        # 🔹 risk_level 수치화
        risk_mapping = {"Low": 0, "Medium": 1, "High": 2}
        df_risk_level["risk_numeric"] = df_risk_level["risk_level"].map(risk_mapping)

        # 🔹 복합 위험도 트렌드 (점 그래프)
        st.markdown("#### 📈 복합 위험도 트렌드 (점 표시)")

        fig = go.Figure()

        # Low (Green)
        low_df = df_risk_level[df_risk_level["risk_level"] == "Low"]
        fig.add_trace(go.Scatter(
            x=low_df["timestamp"],
            y=[0] * len(low_df),
            mode="markers",
            name="Low",
            marker=dict(color="green", size=10)
        ))

        # Medium (Yellow)
        medium_df = df_risk_level[df_risk_level["risk_level"] == "Medium"]
        fig.add_trace(go.Scatter(
            x=medium_df["timestamp"],
            y=[1] * len(medium_df),
            mode="markers",
            name="Medium",
            marker=dict(color="gold", size=10)
        ))

        # High (Red)
        high_df = df_risk_level[df_risk_level["risk_level"] == "High"]
        fig.add_trace(go.Scatter(
            x=high_df["timestamp"],
            y=[2] * len(high_df),
            mode="markers",
            name="High",
            marker=dict(color="red", size=10)
        ))

        fig.update_layout(
            title="📊 복합 위험도 등급 변화 (점 그래프)",
            xaxis_title="시간",
            yaxis=dict(
                title="위험도 등급",
                tickmode="array",
                tickvals=[0, 1, 2],
                ticktext=["Low", "Medium", "High"]
            ),
            height=450
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("복합 위험도 데이터가 없습니다.")


# 🔹 탭 4: anomaly_log
with tabs[3]:
    st.subheader("⚠ anomaly_log")
    st.dataframe(fetch_data("SELECT * FROM anomaly_log ORDER BY timestamp DESC LIMIT 50"))

# 🔹 탭 5: energy_log
with tabs[4]:
    st.subheader("⚡ energy_log")
    st.dataframe(fetch_data("SELECT * FROM energy_log ORDER BY timestamp DESC LIMIT 50"))

# 🔹 탭 6: sensor_error_log
with tabs[5]:
    st.subheader("💥 sensor_error_log (센서 이상 기록)")
    if not df_sensor_error.empty:
        st.dataframe(df_sensor_error)
    else:
        st.warning("센서 이상 로그가 없습니다.")

# ✅ 대기 후 강제 새로고침
time.sleep(REFRESH_INTERVAL)
st.rerun()

