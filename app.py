from re import template
import streamlit as st
import pandas as pd
from datetime import datetime
from main import generate_insight, query_perplexity, send_whatsapp_template
from kite_data import get_reliance_data, get_nifty_data

st.set_page_config(page_title="📈 Nifty AI Insight", layout="centered", initial_sidebar_state="collapsed")

st.markdown("## 🤖 Nifty AI Insight Assistant")
st.markdown("Get smart, real-time market insights using OpenAI + Perplexity + WhatsApp 🚀")

# 🎯 Select stock
stock = st.selectbox("Choose Stock:", ["Reliance", "Bank Nifty"])

if st.button("🧠 Run AI Analysis"):
    with st.spinner("Fetching chart and generating insights..."):

        df = get_reliance_data() if stock == "Reliance" else get_nifty_data()

        if df.empty:
            st.error("❌ No data found.")
        else:
            st.success(f"✅ Data loaded for {stock} ({len(df)} records)")
            st.markdown(f"📅 **Last Updated:** `{datetime.now().strftime('%d-%b-%Y %H:%M:%S')}`")

            st.subheader("📊 Recent Chart Data")
            st.dataframe(df.tail(10), use_container_width=True)

            # 🔍 Generate insights
            insight = generate_insight(df)
            recent = df.tail(30 if stock == "Reliance" else 3).to_dict(orient="records")

            perplexity_prompt = f"""
            Based on the last {'1 month' if stock == 'Reliance' else '3 candles'} of {stock} price action and recent news,
            do you see any buy/sell recommendation? Justify briefly.

            Chart Data:
            {recent}
            """

            context = query_perplexity(perplexity_prompt)

            # 🧠 Show insights in boxes
            st.markdown("### 📈 AI Generated Technical Insight")
            st.info(insight)

            st.markdown("### 📰 Market Context via Perplexity")
            st.warning(context)

            # 📩 WhatsApp send
            final_msg = f"""📈 {stock} AI Insight:
{insight}

📰 Context:
{context}
"""
            if st.button("📲 Send via WhatsApp"):
                send_whatsapp_template(insight, context)
                st.success("✅ Message sent via WhatsApp!")

