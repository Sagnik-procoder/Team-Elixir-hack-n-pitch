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

prompt=PromptTemplate(
    input_variables=['food_type','duration','quantity'],
    template=('you are a smart food waste managment ai agent,people will tell if they have any' \
    'extra food you will telll them what to do with it...first cheack food type\n{food_type}\nduration:{duration} and analysis'
    'if the food is safe for eating if not safe then tell then why it is dangorus and what it we do with it,'
    'if safe then cheack is it not efficiant to feed more than 10 peoples\n quantity:{quantity} then tell them '
    'donate it to local beggers or street dogs if not then tell them we will connect with to local ngos who freely donate foods')
)

chain=prompt |chatmodel

prompt2=PromptTemplate(
    input_variables=['food_type','duration','quantity'],
    template=('you are a smart food waste managment ai agent,analyse the users input\n food_type:{food_type}\n duration of food how much time befor the food is cooked' \
    '\n{duration}\n and cheack if the food is avalable to feed atleast 10 people..if all the critiria filled only give the output in yes other wise no...' \
    'dont give any other output strictly follow yes or no')
)
chain2=prompt2 |chatmodel

def send_email_to_ngo(ngo_email, food_info):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
 
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = ngo_email
    msg['Subject'] = "Food Donation Alert 🍱"

    body = f"Dear NGO Team,\n\nWe have a food donation available:\n{food_info}\n\nPlease collect it soon."
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

def process_food_donation(food_type, duration, quantity, user_location):
    response = chain2.invoke({
        "food_type": food_type,
        "duration": duration,
        "quantity": quantity
    })
    result = response.content[0].text.strip().lower()
    print("AI Decision:", result)

   
    if result == "yes":
       
        nearby_ngos = db['doctors']
        if nearby_ngos:
            for ngo in nearby_ngos:
                send_email_to_ngo(ngo['email'], f"Food: {food_type}, Quantity: {quantity},userLocation:{userRealLoc}")
            return f"✅ Food is suitable. Email sent to {len(nearby_ngos)} nearby NGO(s)."
        else:
            return "⚠️ Food is suitable, but no NGO found near your location."
    else:
        return "❌ Food not suitable for donation."

output = process_food_donation("rice and curry", "2 hours", "15 plates", "Kolkata")
print(output)



