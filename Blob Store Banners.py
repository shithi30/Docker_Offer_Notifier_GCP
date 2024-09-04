# import
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
from google.cloud import storage
import os
import json
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from dotenv import load_dotenv

# env.
load_dotenv()

# pref.
chrome_options = Options()
chrome_options.add_argument("no-sandbox")
chrome_options.add_argument("headless")
chrome_options.add_argument("disable-dev-shm-usage")

# open window
driver = webdriver.Chrome(options = chrome_options)
driver.maximize_window()

# creds
creds_path = "blob_storage_gcp_key.json"
with open(creds_path, "w") as file: json.dump(json.loads(os.getenv("GCP_BLOB_KEY_JSON")), file)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = creds_path

# init.
storage_client = storage.Client()

# banners - acc.
platforms = ["https://www.safeway.ca/", "https://www.foodland.ca/", "https://www.freshco.com/", "https://www.sobeys.com/"]
img_links = set()

# banners - fetch
for platform in platforms:
    driver.get(platform)
    try: soup = BeautifulSoup(driver.page_source, "html.parser").find("div", attrs = {"class": "slick-list draggable"}).find_all("img")
    except: continue
    for s in soup: img_links.add(s["src"])
    print("Fetched banners from: " + platform)

# list blobs in bucket
def list_blobs(bucket_name):
    blobs_list = storage_client.list_blobs(bucket_name)
    blobs_list = [blob.name for blob in blobs_list]
    return blobs_list
    
# empty bucket
def empty_bucket(bucket_name):
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    for blob in blobs: blob.delete()

# url > content > blob
def upload_url_blob(url, bucket_name, blob_name):
    image_data = requests.get(url).content
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(image_data, content_type = "image/jpg")

# download blob
def download_blob(bucket_name, source_blob_name, destination_file_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

# existing banners
banners_historical = list_blobs("bucket_banners_grocery")
banners_old_md5val = [storage_client.bucket("bucket_banners_grocery").get_blob(banner_old).md5_hash for banner_old in banners_historical]

# start afresh
empty_bucket("bucket_banners_grocery_present")

# update
img_links = [link for link in img_links]
banner_count = len(img_links)
for i in range(0, banner_count):

    # filename
    banner_now = "banner_" + str(i + 1) + "_" + time.strftime("%d-%b-%y") + "_" + img_links[i].split("/")[2].split(".")[-2] + ".jpg"

    # upload to present
    upload_url_blob(img_links[i], "bucket_banners_grocery_present", banner_now)

    # check if new
    if_found = 0
    banner_new_md5val = storage_client.bucket("bucket_banners_grocery_present").get_blob(banner_now).md5_hash
    for banner_old_md5val in banners_old_md5val:
        if banner_old_md5val == banner_new_md5val:
            if_found = 1
            break

    # record if new
    if if_found == 0: 
        print("New banner: " + img_links[i])
        upload_url_blob(img_links[i], "bucket_banners_grocery", banner_now)
        download_blob("bucket_banners_grocery_present", banner_now, banner_now)

# close window
driver.close()

# email
sender_email = "shithi30@gmail.com"
recivr_email = ["shithi30@outlook.com"]

# object
msg = MIMEMultipart()
msg["Subject"] = "New Grocery Banners!"
msg["From"] = "Shithi Maitra"
msg["To"] = ", ".join(recivr_email)

# body
body = '''New banners detected, find offers in attachments.<br><br>Thanks,<br>Shithi Maitra<br>Ex Asst. Manager, CS Analytics<br>Unilever BD Ltd.<br>'''
msg.attach(MIMEText(body, "html"))

# attach
files_to_attach = [filename for filename in os.listdir() if filename.endswith(".jpg")]
for file_path in files_to_attach:
    part = MIMEBase("application", "octet-stream")
    with open(file_path, "rb") as attachment: part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(file_path)}")
    msg.attach(part)

# send
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(sender_email, os.getenv("EMAIL_PASS"))
    if len(files_to_attach) > 0: server.sendmail(sender_email, recivr_email, msg.as_string())

