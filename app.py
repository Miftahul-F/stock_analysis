import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

st.set_page_config(page_title="IDX Swing Engine PRO++", layout="centered")

st.title("📊 IDX Swing Decision Engine PRO++ (Time + Price + Risk)")

# ================= INPUT =================
stock = st.text_input("Saham (contoh: BBCA.JK)", "SCNP.JK").upper()

avg_price = float(st.number_input("Average Price", value=220.0))
current_price = float(st.number_input("Current Price", value=190.0))
lots = int(st.number_input("Jumlah Lot Saat Ini", value=4))

buy_date = st.date_input("Tanggal Beli", value=date.today())
today_date = date.today()

capital = float(st.number_input("Total Modal Trading (Rp)", value=10000000.0))
risk_tolerance = float(st.slider("Risk per Trade (%)", 1.0, 5.0, 2.0))

timeframe = st.selectbox(
    "Timeframe",
    ["2-4 minggu", "1-2 minggu"]
)

st.divider()

if st.button("Analyze Position"):

    # ================= TIME CALCULATION =================
    holding_days = (today_date - buy_date).days

    if timeframe == "2-4 minggu":
        max_days = 28
    else:
        max_days = 14

    time_ratio = holding_days / max_days

    # ================= AUTO HIGH LOW =================
    auto_mode = False

    try:
        data = yf.download(
            stock,
            period="2mo",
            interval="1d",
            auto_adjust=True,
            progress=False
        )

        if data is not None and not data.empty and len(data) >= 20:
            recent = data.tail(20)
            high_20 = float(recent["High"].max())
            low_20 = float(recent["Low"].min())
            auto_mode = True
        else:
            raise Exception("Not enough data")

    except:
        st.warning("Yahoo data tidak tersedia. Masukkan High-Low manual.")
        high_20 = float(st.number_input("High 20 Hari Terakhir", value=205.0))
        low_20 = float(st.number_input("Low 20 Hari Terakhir", value=175.0))
        auto_mode = False

    if high_20 <= low_20:
        st.error("High harus lebih besar dari Low.")
        st.stop()

    # ================= VOLATILITY =================
    range_20 = high_20 - low_20
    volatility_pct = (range_20 / current_price) / 4 * 100
    atr = current_price * (volatility_pct / 100)

    # ================= TREND DETECTION =================
    upper_zone = low_20 + 0.6 * range_20
    lower_zone = low_20 + 0.4 * range_20

    if current_price > upper_zone:
        trend_bias = "Bullish"
    elif current_price < lower_zone:
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
    rr_ratio = reward / risk if risk > 0 else 0

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

    if time_ratio > 1:
        score -= 2

    # ================= DECISION =================
    if trend_bias == "Bearish" and loss_pct < -15:
        decision = "❌ CUT LOSS"
        explanation = "Trend bearish + drawdown dalam."
    elif time_ratio > 1 and trend_bias != "Bullish":
        decision = "⏳ TIME STOP EXIT"
        explanation = "Melewati batas waktu swing tanpa breakout."
    elif score >= 5:
        decision = "✅ HOLD / ADD ON STRENGTH"
        explanation = "Struktur dan risk-reward mendukung."
    elif 3 <= score < 5:
        decision = "⚠️ HOLD WITH CAUTION"
        explanation = "Masih layak, tapi disiplin stop."
    else:
        decision = "🚨 EXIT ON BOUNCE"
        explanation = "Struktur lemah."

    # ================= OUTPUT =================
    st.subheader("⏳ Time Analysis")
    st.write(f"Holding Days: {holding_days} hari")
    st.write(f"Max Days (sesuai timeframe): {max_days} hari")

    if time_ratio > 1:
        st.error("⚠️ Sudah melewati timeframe ideal.")
    elif time_ratio > 0.75:
        st.warning("⏳ Mendekati batas waktu swing.")
    else:
        st.success("Masih dalam batas waktu normal.")

    st.divider()

    st.subheader("🔎 Technical Range")
    st.write(f"Mode: {'Auto Yahoo (20D)' if auto_mode else 'Manual'}")
    st.write(f"Trend Detected: {trend_bias}")
    st.write(f"High 20 Hari: {high_20:.2f}")
    st.write(f"Low 20 Hari: {low_20:.2f}")
    st.write(f"Estimated Volatility: {volatility_pct:.2f}%")

    st.divider()

    st.subheader("📊 Risk Model")
    st.write(f"Loss dari average: {loss_pct:.2f}%")
    st.write(f"Stop Loss: {stop_loss:.2f}")
    st.write(f"Target: {target_price:.2f}")
    st.write(f"Risk/Reward Ratio: {rr_ratio:.2f}")

    st.divider()

    st.subheader("📌 Final Decision")
    st.success(decision)
    st.write(explanation)
    st.write(f"Score: {score}/6")

    # ================= POSITION RISK =================
    position_value = current_price * lots * 100
    floating_loss_value = (current_price - avg_price) * lots * 100
    max_risk_allowed = capital * (risk_tolerance / 100)
    risk_if_stop = (current_price - stop_loss) * lots * 100

    st.divider()
    st.subheader("💰 Position Risk")

    st.write(f"Position Value: Rp {position_value:,.0f}")
    st.write(f"Floating P/L: Rp {floating_loss_value:,.0f}")
    st.write(f"Risk if Stop Hit: Rp {risk_if_stop:,.0f}")
    st.write(f"Max Risk Allowed: Rp {max_risk_allowed:,.0f}")

    if risk_if_stop > max_risk_allowed:
        st.error("⚠️ Posisi terlalu besar untuk risk tolerance Anda.")
    else:
        st.success("Ukuran posisi masih dalam batas aman.")

    # ================= MAX ADD LOT =================
    risk_per_lot = (current_price - stop_loss) * 100
    if risk_per_lot > 0:
        additional_lots_allowed = int((max_risk_allowed - risk_if_stop) / risk_per_lot)
        if additional_lots_allowed > 0:
            st.write(f"Lot tambahan maksimal aman: {additional_lots_allowed}")
        else:
            st.write("Tidak disarankan menambah lot.")

    st.divider()

    # ================= SIMULATION =================
    st.subheader("📈 Price Projection")
    simulated_prices = np.linspace(stop_loss, target_price, 50)

    plt.figure()
    plt.plot(simulated_prices)
    plt.axhline(avg_price, linestyle='--')
    plt.axhline(current_price, linestyle=':')
    plt.title("Projected Price Range")
    st.pyplot(plt)

    st.markdown("---")
    st.markdown("⚠️ Decision support tool. Bukan sinyal absolut.")