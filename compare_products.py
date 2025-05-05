import google.generativeai as genai
from graphql import get_shopify_data
import streamlit as st

# Configure Gemini

API_KEY = st.secrets["GEMINI"]["GEMINI_KEY"]
genai.configure(api_key=API_KEY)

def compare(filename, shopify_data):
    
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    prompt = f"""
You are a wine data matching expert.

The product we are checking (X) is provided in the following format:
"Vintage - Producer - Appellation/Region - Grape Variety"

Product X:
"{filename}"

Below is the product catalog from Shopify (may have inconsistent or unstructured formatting):

{shopify_data}

Rules:
- Match ONLY if all 4 components (Vintage, Producer, Region, Grape Variety) match.
- Be strict about the VINTAGE (year). If the year differs, it's NOT a match.
- Return:
  - "1" if X is an exact match in the Shopify data.
  - "0" if not.
- DO NOT explain or add anything else.

Respond with only "1" or "0".
"""

    response = model.generate_content(prompt)
    result = response.text.strip()

    return "File Match Successfull, Uploaded to Shopify" if result == "1" else "Needs Human Review"

# Test example
# shopify_data = get_shopify_data()
# filename = "2016 Piedrasassi Santa Maria Valley Syrah"
# response = compare(filename, shopify_data)
# print("Match Result:", response)
