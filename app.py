import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt

st.set_page_config(page_title="Swing Engine PRO", layout="centered")

st.title("📊 Swing Decision Engine PRO (2–4 Weeks)")

# ================= INPUT =================
stock = st.text_input("Saham (contoh: SCNP.JK)", "SCNP.JK")
avg_price = st.number_input("Average Price", value=220.0)
timeframe = st.selectbox("Timeframe", ["2-4 minggu", "1-2 minggu"])

if st.button("Analyze Position"):

    try:
        data = yf.download(stock, period="6mo", interval="1d")
        data.dropna(inplace=True)

        current_price = data["Close"].iloc[-1]

        # ===== INDICATORS =====
        data["EMA20"] = data["Close"].ewm(span=20).mean()
        data["EMA50"] = data["Close"].ewm(span=50).mean()

        # ATR
        high_low = data["High"] - data["Low"]
        high_close = np.abs(data["High"] - data["Close"].shift())
        low_close = np.abs(data["Low"] - data["Close"].shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(14).mean().iloc[-1]

        ema20 = data["EMA20"].iloc[-1]
        ema50 = data["EMA50"].iloc[-1]

        # ===== TREND ANALYSIS =====
        bullish_trend = current_price > ema20 > ema50
        bearish_trend = current_price < ema20 < ema50

        # ===== VOLATILITY STOP =====
        stop_loss = current_price - (1.5 * atr)
        target_price = current_price + (2.5 * atr)

        risk = current_price - stop_loss
        reward = target_price - current_price
        rr_ratio = reward / risk if risk != 0 else 0

        loss_from_avg = (current_price - avg_price) / avg_price * 100

        # ===== SCORING SYSTEM =====
        score = 0

        if bullish_trend:
            score += 2
        if not bearish_trend:
            score += 1
        if rr_ratio >= 1.5:
            score += 2
        if loss_from_avg > -15:
            score += 1

        # ===== DECISION LOGIC =====
        if bearish_trend and loss_from_avg < -15:
            decision = "❌ CUT LOSS"
            bias = "Bearish Structure"
        elif score >= 5:
            decision = "✅ HOLD / ADD ON STRENGTH"
            bias = "Bullish Bias"
        elif 3 <= score < 5:
            decision = "⚠️ HOLD WITH CAUTION"
            bias = "Neutral Bias"
        else:
            decision = "🚨 EXIT ON BOUNCE"
            bias = "Weak Structure"

        # ===== OUTPUT =====
        st.subheader("🔎 Market Data")
        st.write(f"Current Price: {current_price:.2f}")
        st.write(f"EMA20: {ema20:.2f}")
        st.write(f"EMA50: {ema50:.2f}")
        st.write(f"ATR (14): {atr:.2f}")

        st.divider()

        st.subheader("📊 Risk Model")
        st.write(f"Suggested Stop (ATR based): {stop_loss:.2f}")
        st.write(f"Projected Target: {target_price:.2f}")
        st.write(f"Risk/Reward Ratio: {rr_ratio:.2f}")
        st.write(f"Loss from Average: {loss_from_avg:.2f}%")

        st.divider()

        st.subheader("📌 Final Decision")
        st.success(decision)
        st.write(f"Bias: {bias}")
        st.write(f"Score: {score}/6")

        st.divider()

        st.subheader("📈 Chart")
        plt.figure()
        plt.plot(data["Close"])
        plt.plot(data["EMA20"])
        plt.plot(data["EMA50"])
        st.pyplot(plt)

    except:
        st.error("Symbol tidak ditemukan. Gunakan format .JK untuk saham Indonesia.")