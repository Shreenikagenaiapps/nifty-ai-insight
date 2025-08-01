from openai import OpenAI
from twilio.rest import Client
from mock_data import get_mock_data
import json  # ✅ Added for template variable support

from config import (
    OPENAI_API_KEY,
    TWILIO_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM,
    TWILIO_WHATSAPP_TO,
    PERPLEXITY_API_KEY
)
from kite_data import get_nifty_data
from kite_login import get_login_url, generate_session, load_access_token
import requests

access_token = load_access_token()

if not access_token:
    print("🔗 Login URL:", get_login_url())
    request_token = input("📥 Enter request token from URL: ").strip()
    access_token = generate_session(request_token)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def generate_insight(dataframe):
    recent = dataframe.tail(30).to_dict(orient='records')

    prompt = f"""
    You are a professional stock trading analyst.
    Analyze the Nifty 15 min chart data and suggest the trend:

    {recent}

    Rules:
    - Keep the tone professional.
    - Do not use slang.
    - Limit to 40 words.
    - Focus on price action, trend, or volume.
    - If a buy opportunity is visible (e.g., strong bounce, bullish engulfing, key support), suggest buying and specify approximate entry zone.
    - If no clear entry, say to wait or avoid.
    - Do NOT make up data not in the candles.
    - Do not use financial jargon like “RSI”, “MACD” unless visible from price alone.

    Give:
    1. A brief insight (trend or pattern).
    2. Ideal entry point for trade (buy/sell).
    3. Suggested stop-loss (SL).
    4. Mention whether trade should be avoided if not clear.

    Format your response as:
    Insight: ...
    Entry: ...
    SL: ...
    AvoidTrade: Yes/No
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content
        return content.strip() if content else "⚠️ No response received from OpenAI."

    except Exception as e:
        print("OpenAI Error:", e)
        return "⚠️ Failed to generate insight due to API error."

def query_perplexity(prompt):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": "You are a helpful financial assistant that uses real-time web context."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        print("❌ Perplexity API Error:", e)
        if hasattr(e, "response") and e.response and hasattr(e.response, "text"):
            print("❌ Response Text:", e.response.text)
        else:
            print("❌ No response body received.")
        return "⚠️ Failed to fetch context from Perplexity."

# ✅ REPLACED send_whatsapp with this version using approved template
def send_whatsapp_template(insight_text, context_text):
    if not all([TWILIO_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, TWILIO_WHATSAPP_TO]):
        print("❌ Missing Twilio credentials.")
        return

    twilio_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

    try:
        twilio_client.messages.create(
            from_=TWILIO_WHATSAPP_FROM,
            to=TWILIO_WHATSAPP_TO,
            content_sid='HXbb859a20bbd79402b0b7c240c753fbc9',  # Replace this!
            content_variables=json.dumps({
                '1': insight_text,
                '2': context_text
            })
        )
        print("✅ WhatsApp template message sent!")
    except Exception as e:
        print("❌ Failed to send WhatsApp template:", e)


if __name__ == "__main__":
    df = get_nifty_data()
    insight = generate_insight(df)

    recent = df.tail(30).to_dict(orient='records')
    perplexity_prompt = f"""
    Based on the last 15 min of Nifty chart price action and recent market news, is there any suggestion to invest?

    Chart data:
    {recent}

    Do you see any market news, macro events, or technical confirmations that support a buy/sell recommendation for Nifty now? Be concise.
    """

    context = query_perplexity(perplexity_prompt)

    final_message = f"""
📈 OpenAI Technical Insight:
{insight}

📰 Perplexity Market Context:
{context}
"""

    print("📊 Data is:", df)
    print("📊 Insight:", insight)
    print("🧠 Perplexity Insight:", context)

    # ✅ Use Twilio template-based message sending
    if len(final_message) > 1500:
        final_message = final_message[:1500] + "...\n⚠️ Message trimmed due to WhatsApp limit."

    # WhatsApp template has a hard limit of 1600 characters
    MAX_LENGTH = 1500

    # Trim each individually to fit within limit when combined
    if len(insight) > 700:
        insight = insight[:700] + "...\n⚠️ Trimmed"

    if len(context) > 700:
        context = context[:700] + "...\n⚠️ Trimmed"

    send_whatsapp_template(insight,context)
