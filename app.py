import streamlit as st
import pandas as pd
from main import generate_insight, query_perplexity, send_whatsapp_template
from kite_data import get_reliance_data, get_nifty_data

st.set_page_config(page_title="📊 Stock Insight AI", layout="centered")

st.title("🤖 Stock Insight Assistant")

stock = st.selectbox("📍 Select Stock", ["Reliance", "Nifty"])

if st.button("🧠 Run AI Analysis"):
    st.info("⏳ Fetching chart data and generating insights...")

    # Fetch data based on selection
    df = get_reliance_data() if stock == "Reliance" else get_nifty_data()

    if df.empty:
        st.error("❌ Failed to fetch chart data.")
    else:
        st.subheader(f"📈 {stock} - Recent Candles")
        st.dataframe(df.tail(30 if stock == "Reliance" else 3), use_container_width=True)

        insight = generate_insight(df)
        recent = df.tail(30 if stock == "Reliance" else 3).to_dict(orient="records")

        perplexity_prompt = f"""
        Based on the last {'1 month' if stock == 'Reliance' else '3 candles'} of {stock} price action and latest market news:
        {recent}

        Is there any news or macroeconomic factor supporting a buy/sell recommendation now? Keep it concise.
        """
        context = query_perplexity(perplexity_prompt)

        st.subheader("🧠 OpenAI Technical Insight")
        st.code(insight, language="markdown")

        st.subheader("📡 Perplexity Market Context")
        st.code(context, language="markdown")

        final_message = f"""📈 {stock} AI Insight:
{insight}

📰 Context:
{context}
"""

        if st.button("📲 Send Insight via WhatsApp"):
            send_whatsapp_template(insight, context)
            st.success("✅ Sent to WhatsApp!")
