from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account
import json
import os
import streamlit as st

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = st.secrets["DRIVE"]

JSON_PATH = "folder_id.json"

def authenticate():
    """Authenticate with the client’s service account."""
    creds = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
    return creds

def create_folder(folder_name, parent_folder_id=None, share_with=None, role='writer'):
    """
    Create a folder in Drive.
    If parent_folder_id is given, it’s created inside that folder.
    If share_with (an email) is provided, the folder is shared with that user.
    Returns the new folder’s ID.
    """
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    # 1) create folder
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    if parent_folder_id:
        metadata['parents'] = [parent_folder_id]

    folder = service.files().create(
        body=metadata,
        fields='id'
    ).execute()
    folder_id = folder['id']
    print(f"Folder created: {folder_id}")

    # 2) optionally share it so you can see it in your own Drive
    if share_with:
        perm = {
            'type': 'user',
            'role': role,
            'emailAddress': share_with
        }
        service.permissions().create(
            fileId=folder_id,
            body=perm,
            fields='id'
        ).execute()
        print(f"Folder {folder_id} shared with {share_with} as {role}")
    print("Created Folder")
    return folder_id

def upload_file_to_folder(file_path, filename, folder_id):
    """
    Upload a local file to the specified Drive folder.
    Returns the uploaded file’s ID.
    """
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    media = MediaFileUpload(file_path, resumable=True)
    metadata = {
        'name': filename,
        'parents': [folder_id]
    }

    file = service.files().create(
        body=metadata,
        media_body=media,
        fields='id'
    ).execute()
    print(f"Uploaded {filename} → {file['id']}")


# def get_images(folder_id):
#     creds = authenticate()
#     service = build('drive', 'v3', credentials=creds)

#     # List files in the specified folder
#     results = service.files().list(
#         q=f"'{folder_id}' in parents and (mimeType='image/jpeg' or mimeType='image/png')",  # Filter for image types
#         fields="files(id, name, mimeType)"
#     ).execute()

#     items = results.get('files', [])

#     if not items:
#         print("No images found.")
#         return []

#     # Collecting image details
#     image_files = []
#     for item in items:
#         image_files.append({
#             'id': item['id'],
#             'name': item['name'],
#             'mimeType': item['mimeType']
#         })
#         print(f"Found image: {item['name']} (ID: {item['id']})")

#     return image_files

def delete_file(file_id, user_email):
    """
    Delete a file from Drive by its ID.
    """
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    service.files().delete(fileId=file_id).execute()
    print(f"Deleted file {file_id}")

    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            folder_data = json.load(f)
    else:
        folder_data = {}

    del folder_data[user_email]

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(folder_data, f, indent=2, ensure_ascii=False)


# create & share
def create_wine_folders(share_id):
    """
    Ensures that for this user (share_id) we have a top-level parent
    folder plus the four subfolders in folder_id.json under a single key.
    """

    # 1) Load existing data
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            folder_data = json.load(f)
    else:
        folder_data = {}

    # 2) If this user already has entries, skip creation
    if share_id in folder_data:
        return

    # 3) Create the Drive folders
    parent_name = f"WINE LABEL OCR ({share_id})"
    parent_id = create_folder(parent_name, share_with=share_id)

    input_id    = create_folder("INPUT",            parent_id, share_with=share_id)
    output_id   = create_folder("OUTPUT",           parent_id, share_with=share_id)
    nhr_id      = create_folder("Need Human Review",parent_id, share_with=share_id)
    uploaded_id = create_folder("Uploaded",         parent_id, share_with=share_id)

    # 4) Insert into our dict under the user's email key
    folder_data[share_id] = {
        parent_name: parent_id,
        "INPUT":    input_id,
        "OUTPUT":   output_id,
        "NHR":      nhr_id,
        "UPLOADED": uploaded_id
    }

    # 5) Write back
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(folder_data, f, indent=2, ensure_ascii=False)

# def get_folder_id(folder_name):
#     """
#     Read folder_id.json and return the ID for folder_name,
#     or None if the file or key doesn’t exist.
#     """
#     json_path = os.path.join(os.getcwd(), "folder_id.json")
#     # If the JSON file doesn't exist, return None
#     if not os.path.exists(json_path):
#         return None

#     with open(json_path, "r", encoding="utf-8") as f:
#         data = json.load(f)

#     folder_id = data.get(folder_name)
#     if folder_id:
#         return folder_id
#     else:
#         return None
    

# def find_folder_id_by_name(folder_name, parent_folder_id=None):
#     """
#     Returns the ID of the first folder matching folder_name under the given parent,
#     or None if no such folder exists.
#     """
#     creds = authenticate()
#     service = build('drive', 'v3', credentials=creds)

#     # Build the query: by mimeType + name, plus optionally parent
#     q = "mimeType='application/vnd.google-apps.folder' and name='%s'" % folder_name.replace("'", "\\'")
#     if parent_folder_id:
#         q += " and '%s' in parents" % parent_folder_id

#     resp = service.files().list(q=q, fields='files(id, name)', pageSize=1).execute()
#     items = resp.get('files', [])
#     return items[0]['id'] if items else None


# def list_all_folders():
#     """
#     Return a list of all Drive folders (ID and name) visible to the service account.
#     """
#     creds = authenticate()
#     service = build('drive', 'v3', credentials=creds)

#     folders = []
#     page_token = None

#     # Paginate through all folders
#     while True:
#         response = service.files().list(
#             q="mimeType='application/vnd.google-apps.folder' and trashed=false",
#             spaces='drive',
#             fields='nextPageToken, files(id, name)',
#             pageToken=page_token
#         ).execute()

#         for f in response.get('files', []):
#             folders.append({'id': f['id'], 'name': f['name']})

#         page_token = response.get('nextPageToken')
#         if not page_token:
#             break

#     return folders


# delete_file("1lzHTUnG-NPla5uu6ITzJFH3sgSWcTm1L")