import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

st.set_page_config(page_title="Smart Waste Management Assistant", layout="wide")

st.title("♻️ Smart Waste Management Assistant")
st.markdown("### Get guidance on waste issues and automatically alert your local authorities if needed.")

chatmodel = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

client = MongoClient("mongodb+srv://demouse:rupam2629@cluster0.ylqzjet.mongodb.net/mental_health?retryWrites=true&w=majority&appName=Cluster0")
db = client['mental_health']
doctors = db['doctors']

prompt = PromptTemplate(
    input_variables=['query'],
    template=(
        'You are a waste management guide. Read the query and guide the user '
        'on how to manage the waste efficiently in under 300 words.\n\nQuery: {query}'
    )
)

prompt2 = PromptTemplate(
    input_variables=['query', 'location'],
    template=(
        'The user will provide a problem and their location. '
        'If the area seems highly polluted or has poor waste management, '
        'give only the email address of the local municipal corporation. '
        'If no action is needed, just reply "No action needed".\n\n'
        'Query: {query}\nLocation: {location}'
    )
)

query = st.text_area("📝 Describe your waste management problem", height=120)
location = st.text_input("📍 Enter your location (e.g., South Kolkata, Delhi)")

if st.button("Analyze & Notify"):
    if not query or not location:
        st.warning("⚠️ Please enter both the query and location before proceeding.")
    else:
        with st.spinner("Analyzing your query..."):
            chain1 = prompt | chatmodel
            chain2 = prompt2 | chatmodel

            advice = chain1.invoke({'query': query}).content
            email_output = chain2.invoke({'query': query, 'location': location}).content

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("🧭 Guidance")
            st.write(advice)

        with col2:
            st.subheader("🏢 Corporation Email")
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', email_output)
            if email_match:
                email_address = email_match.group(0)
                st.success(f"📧 {email_address}")
            else:
                st.info("No valid email detected.")

        with col3:
            st.subheader("📤 Email Status")
            if email_match:
                sender_email = os.getenv("SENDER_EMAIL") or "yourgmail@gmail.com"
                app_password = os.getenv("APP_PASSWORD") or "your-app-password"

                subject = "Waste Management Complaint"
                body = f"""
                Dear Municipal Corporation,

                This is to report a waste management issue:
                "{query}"

                Location: {location}
                Kindly take appropriate action.

                Regards,
                Concerned Citizen
                """

                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = email_address
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                try:
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                        server.login(sender_email, app_password)
                        server.send_message(msg)
                    st.success(f"✅ Email sent successfully to {email_address}")
                except Exception as e:
                    st.error(f"❌ Failed to send email: {e}")
            else:
                st.info("📨 Email not sent (no valid email detected).")
