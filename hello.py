import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv() 
sample_pass = os.getenv("SAMPLE_PASSWORD")
print(sample_pass)

print("Hello from Docker!")

response = requests.get('https://api.github.com')
print(f"GitHub API status: {response.status_code}")

data = {'Name': ['Alice', 'Bob'], 'Age': [25, 30]}
df = pd.DataFrame(data)
print(df) 