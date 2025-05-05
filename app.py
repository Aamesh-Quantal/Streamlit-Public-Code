import streamlit as st
import os
import time
from PIL import Image
from removebg import remove_bg
from ocr import getText, categorizeText
from compare_products import compare
import io
import file_management
import json
from graphql import get_shopify_data

shopify_data = get_shopify_data()
st.title("Wine Label OCR & Background Removal")

# 1) Step One: collect images
st.markdown("## 1. Upload Wine Label Images")
uploaded_files = st.file_uploader(
    "Drag & drop your wine label images here",
    type=["jpg","jpeg","png"],
    accept_multiple_files=True
)

local_paths = []
if uploaded_files:
    os.makedirs("temp", exist_ok=True)
    for up in uploaded_files:
        save_path = os.path.join("temp", up.name)
        with open(save_path, "wb") as f:
            f.write(up.getbuffer())
        st.write(f"✅ Saved upload to `{save_path}`")
        local_paths.append((up.name, save_path))

# 2) Only once we have at least one image, ask for the email and setup Drive
if local_paths:
    st.markdown("## 2. Enter Your Google Account Email")
    user_email = st.text_input("Enter your email id to save & retrieve images:", "")
    if user_email:
        folder_name = f"WINE LABEL OCR ({user_email})"
        JSON_PATH = "folder_id.json"

        with st.spinner("Processing…"):
            # load existing IDs
            if os.path.exists(JSON_PATH):
                with open(JSON_PATH, "r", encoding="utf-8") as f:
                    folder_data = json.load(f)
            else:
                folder_data = {}

            # only create if missing
            if user_email not in folder_data:
                file_management.create_wine_folders(user_email)
                with open(JSON_PATH, "r", encoding="utf-8") as f:
                    folder_data = json.load(f)

        parent_id = folder_data[user_email][folder_name]

        st.markdown(f"""
    **Next Steps:**  
    1. In Google Drive go to [Shared with me](https://drive.google.com/drive/folders/{parent_id})  
    2. You’ll see **WINE LABEL OCR** with subfolders: INPUT / OUTPUT / UPLOADED / NEED HUMAN REVIEW  
    3. We’ll now upload your images into the INPUT folder and process them.
    """)


        # 3) Upload the raw files into the Drive INPUT folder
        with st.spinner("Processing…"):
            input_id = folder_data[user_email]["INPUT"]
            for name, path in local_paths:
                file_management.upload_file_to_folder(path, name, input_id)
                st.write(f"📤 Uploaded `{name}` to Drive INPUT folder.")

            # 4) Process locally & offer “Save as …” for OUTPUT
            SAVE_DIR = "temp/processed"
            os.makedirs(SAVE_DIR, exist_ok=True)

            for filename, path in local_paths:
                st.subheader(f"Processing: {filename}")
                before = time.time()

                # 4a) Background removal (or mock)
                # processed_bytes = io.BytesIO(open(path, "rb").read())
                processed_bytes = remove_bg(path)

                st.image(processed_bytes, caption="Background Removed", use_container_width=True)

                # 4b) OCR & structuring
                with st.spinner("Processing…"):
                    img = Image.open(processed_bytes)
                    raw_text = getText(img)
                    structured = categorizeText(raw_text)
                    st.text_area("Extracted & Structured Text", structured, height=150)

                    # 4c) Rename & save
                    suggested = structured.replace('"','').replace("\n"," ").strip() + ".jpg"
                    edited_filename = st.text_input(f"Final filename for {filename}", value=suggested, key=f"fn_{filename}")

                    final_path = os.path.join(SAVE_DIR, edited_filename)
                    with open(final_path, "wb") as f:
                        f.write(processed_bytes.getvalue())
                    # st.success(f"Saved locally as `{final_path}`")

                    # upload to OUTPUT folder
                    output_id = folder_data[user_email]["OUTPUT"]
                    file_management.upload_file_to_folder(final_path, edited_filename, output_id)
                    st.success(f"Uploaded `{edited_filename}` to Drive OUTPUT folder.")
                
                compare_result = compare(edited_filename, shopify_data)
                st.write(compare_result)
                if os.path.exists(JSON_PATH):
                    with open(JSON_PATH, "r", encoding="utf-8") as f:
                        folder_data = json.load(f)

                if compare_result == "File Match Successfull, Uploaded to Shopify":
                    upload_id = folder_data[user_email]["UPLOAD"]
                    file_management.upload_file_to_folder(final_path, edited_filename, upload_id)
                    st.success(f"Uploaded `{edited_filename}` to Drive Upload folder.")

                elif compare_result == "Needs Human Review":
                    nhr_id = folder_data[user_email]["NHR"]
                    file_management.upload_file_to_folder(final_path, edited_filename, nhr_id)
                    st.write(f"Uploaded `{edited_filename}` to Drive Need Human Review folder.")
                    st.write("Image requires manual approval")

                st.write(f"⏱ Processing time: {time.time() - before:.2f}s")