import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="IDX Swing Engine PRO", layout="centered")

st.title("📊 IDX Swing Decision Engine PRO (2–4 Weeks)")

st.markdown("Masukkan data posisi Anda:")

# ================= INPUT =================
stock = st.text_input("Saham", "SCNP")
avg_price = st.number_input("Average Price", value=220.0)
current_price = st.number_input("Current Price", value=190.0)

volatility_pct = st.slider(
    "Estimasi Volatilitas Harian (%)",
    min_value=1,
    max_value=10,
    value=4
)

trend_bias = st.selectbox(
    "Trend Saat Ini",
    ["Bullish", "Sideways", "Bearish"]
)

timeframe = st.selectbox(
    "Timeframe",
    ["2-4 minggu", "1-2 minggu"]
)

st.divider()

if st.button("Analyze Position"):

    # ================= CALCULATION =================
    loss_pct = (current_price - avg_price) / avg_price * 100

    # ATR estimation
    atr = current_price * (volatility_pct / 100)

    if timeframe == "2-4 minggu":
        stop_loss = current_price - (2 * atr)
        target_price = current_price + (3 * atr)
    else:
        stop_loss = current_price - (1.5 * atr)
        target_price = current_price + (2.5 * atr)

    risk = current_price - stop_loss
    reward = target_price - current_price
    rr_ratio = reward / risk if risk != 0 else 0

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
        explanation = "Struktur bearish + drawdown dalam."
    elif score >= 5:
        decision = "✅ HOLD / ADD ON STRENGTH"
        explanation = "Risk-reward baik dan struktur mendukung."
    elif 3 <= score < 5:
        decision = "⚠️ HOLD WITH CAUTION"
        explanation = "Masih layak, tapi perlu disiplin stop."
    else:
        decision = "🚨 EXIT ON BOUNCE"
        explanation = "Struktur lemah, tunggu rebound untuk keluar."

    # ================= OUTPUT =================
    st.subheader("🔎 Risk Model")
    st.write(f"Loss dari average: {loss_pct:.2f}%")
    st.write(f"ATR Estimasi: {atr:.2f}")
    st.write(f"Suggested Stop Loss: {stop_loss:.2f}")
    st.write(f"Projected Target: {target_price:.2f}")
    st.write(f"Risk/Reward Ratio: {rr_ratio:.2f}")

    st.divider()

    st.subheader("📌 Final Decision")
    st.success(decision)
    st.write(explanation)
    st.write(f"Score: {score}/6")

    st.divider()

    # ================= AVERAGING ENGINE =================
    st.subheader("📉 Averaging Simulation")

    add_lots = st.number_input("Tambah Berapa Lot?", value=0)

    if add_lots > 0:
        total_lots = 4 + add_lots  # default awal 4 lot
        new_avg = ((avg_price * 4) + (current_price * add_lots)) / total_lots
        st.write(f"New Average Price: {new_avg:.2f}")

        breakeven_move = (new_avg - current_price) / current_price * 100
        st.write(f"Perlu kenaikan {breakeven_move:.2f}% untuk BE")

    st.divider()

    # ================= VISUAL SIMULATION =================
    st.subheader("📈 Price Scenario Simulation")

    simulated_prices = np.linspace(stop_loss, target_price, 50)
    plt.figure()
    plt.plot(simulated_prices)
    plt.axhline(avg_price, linestyle='--')
    plt.axhline(current_price, linestyle=':')
    st.pyplot(plt)

    st.markdown("""
    --- 
    ⚠️ Gunakan ini sebagai decision support, bukan sinyal absolut.
    Disiplin risk management tetap nomor satu.
    """)
