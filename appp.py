import streamlit as st
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv()

chatmodel = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY"),
)

client = MongoClient("mongodb+srv://demouse:rupam2629@cluster0.ylqzjet.mongodb.net/mental_health?retryWrites=true&w=majority&appName=Cluster0")
db = client['mental_health']
doctors = db['doctors']

prompt1 = PromptTemplate(
    input_variables=["query"],
    template=(
        "You are a health assistant. The user will give you a query. "
        "Analyze it and tell which kind of doctor is needed. "
        "The output should be only one of the following doctor types — "
        "cardiology dermatology general physician gynecology neurology orthopedics pediatrics psychiatry other. "
        "Do not give any other result. Just give the doctor type only. "
        "Query: {query}"
    )
)

prompt2 = PromptTemplate(
    input_variables=["query"],
    template=(
        "You are a health assistant guide. Read the user query and explain briefly "
        "what could be the possible problem (keep it under 300 words). Query: {query}"
    )
)

st.set_page_config(page_title="AI Health Assistant", page_icon="💊", layout="centered")

st.title("💊 AI Health Assistant")
st.write("Describe your health issue and get doctor recommendations instantly.")

user_query = st.text_area("🧠 Describe your problem:", placeholder="e.g., I have constant headaches and dizziness.")
user_location = st.text_input("📍 Enter your city:", placeholder="e.g., Kolkata")


if st.button("Analyze & Find Doctors"):
    if user_query and user_location:
        with st.spinner("Analyzing your problem..."):
            chain1 = prompt1 | chatmodel
            result = chain1.invoke({'query': user_query})
            doctor_type = result.content.strip().lower()

            chain2 = prompt2 | chatmodel
            problem_summary = chain2.invoke({'query': user_query}).content.strip()

            query = {
                "specialization": doctor_type,
                "location": user_location
            }
            matching_doctors = list(doctors.find(query))

        col1, col2 = st.columns([2,1])

      
        with col1:
            st.subheader("🧠 Problem Details")
            st.info(problem_summary)
            st.write(f"**Suggested Specialist:** {doctor_type.title()}")

       
        with col2:
            st.subheader("👨‍⚕️ Available Doctors")
            if matching_doctors:
                for doc in matching_doctors:
                    name = doc.get("fullName", "Unknown")
                    fees = doc.get("fees", "Not available")
                    apptime = doc.get("availableTime", "Not specified")
                    link = doc.get("link", "#")

                    st.markdown(f"**👨‍⚕️ {name}**")
                    st.write(f"Specialization: {doctor_type.title()}")
                    st.write(f"💰 Fees: ₹{fees}")
                    st.write(f"🕒 Appointment Time: {apptime}")
                    st.markdown(f"[🔗 Book Appointment]({link})", unsafe_allow_html=True)
                    st.markdown("---")
            else:
                st.warning(f"No doctors found in {user_location.title()} for {doctor_type.title()} specialization.")
    else:
        st.error("Please enter both your problem and city.")
