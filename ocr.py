import google.generativeai as genai
from PIL import Image
from prompt import prompts
import streamlit as st

#Gemini key
API_KEY = st.secrets["GEMINI"]["GEMINI_KEY"]

genai.configure(api_key=API_KEY)
def getText(image):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    response = model.generate_content([
        image,
        prompts["text_prompt"]
    ])
    return response.text

def categorizeText(ocr_text):
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    response = model.generate_content([
        f"{prompts['format_prompt']} Below is the text extracted from the bottle:\n{ocr_text}"
    ])

    return response.text
