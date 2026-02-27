import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="IDX Swing Engine Hybrid", layout="centered")

st.title("📊 IDX Swing Decision Engine (Hybrid Auto Mode)")

# ================= INPUT =================
stock = st.text_input("Saham (contoh: BBCA.JK)", "BBCA.JK")
avg_price = st.number_input("Average Price", value=220.0)
current_price = st.number_input("Current Price", value=190.0)

timeframe = st.selectbox(
    "Timeframe",
    ["2-4 minggu", "1-2 minggu"]
)

st.divider()

if st.button("Analyze Position"):

    # ================= TRY AUTO HIGH-LOW =================
    try:
        data = yf.download(stock, period="1mo", interval="1d")
        data.dropna(inplace=True)

        if len(data) < 5:
            raise Exception("Not enough data")

        high_20 = data["High"].max()
        low_20 = data["Low"].min()

        auto_mode = True

    except:
        st.warning("Data Yahoo tidak tersedia. Masukkan High-Low manual.")
        high_20 = st.number_input("High 20 Hari Terakhir", value=205.0)
        low_20 = st.number_input("Low 20 Hari Terakhir", value=175.0)
        auto_mode = False

    # ================= VOLATILITY =================
    range_20 = high_20 - low_20
    volatility_pct = (range_20 / current_price) / 4 * 100
    atr = current_price * (volatility_pct / 100)

    # ================= TREND DETECTION =================
    mid_range = (high_20 + low_20) / 2

    if current_price > mid_range and current_price > (low_20 + 0.6 * range_20):
        trend_bias = "Bullish"
    elif current_price < mid_range and current_price < (low_20 + 0.4 * range_20):
        trend_bias = "Bearish"
    else:
        trend_bias = "Sideways"

    # ================= STOP & TARGET =================
    if timeframe == "2-4 minggu":
        stop_loss = current_price - (2 * atr)
        target_price = current_price + (3 * atr)
    else:
        stop_loss = current_price - (1.5 * atr)
        target_price = current_price + (2.5 * atr)

    risk = current_price - stop_loss
    reward = target_price - current_price
    rr_ratio = reward / risk if risk != 0 else 0

    loss_pct = (current_price - avg_price) / avg_price * 100

    # ================= SCORING =================
    score = 0

    if trend_bias == "Bullish":
        score += 3
    elif trend_bias == "Sideways":
        score += 1

    if rr_ratio >= 1.5:
        score += 2

    if loss_pct > -15:
        score += 1

    # ================= DECISION =================
    if trend_bias == "Bearish" and loss_pct < -15:
        decision = "❌ CUT LOSS"
        explanation = "Trend bearish dan drawdown dalam."
    elif score >= 5:
        decision = "✅ HOLD / ADD ON STRENGTH"
        explanation = "Struktur mendukung dan risk-reward baik."
    elif 3 <= score < 5:
        decision = "⚠️ HOLD WITH CAUTION"
        explanation = "Masih layak, tapi perlu disiplin stop."
    else:
        decision = "🚨 EXIT ON BOUNCE"
        explanation = "Struktur lemah, tunggu rebound untuk keluar."

    # ================= OUTPUT =================
    st.subheader("🔎 Data Range")
    st.write(f"Mode: {'Auto Yahoo' if auto_mode else 'Manual'}")
    st.write(f"High 20 Hari: {high_20:.2f}")
    st.write(f"Low 20 Hari: {low_20:.2f}")
    st.write(f"Estimated Volatility: {volatility_pct:.2f}%")

    st.divider()

    st.subheader("📊 Risk Model")
    st.write(f"Loss dari average: {loss_pct:.2f}%")
    st.write(f"Suggested Stop Loss: {stop_loss:.2f}")
    st.write(f"Projected Target: {target_price:.2f}")
    st.write(f"Risk/Reward Ratio: {rr_ratio:.2f}")

    st.divider()

    st.subheader("📌 Final Decision")
    st.success(decision)
    st.write(explanation)
    st.write(f"Trend Detected: {trend_bias}")
    st.write(f"Score: {score}/6")

    st.markdown("---")
    st.markdown("⚠️ Gunakan sebagai decision support, bukan sinyal absolut.")