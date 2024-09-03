import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv() 
sample_pass = os.getenv("SAMPLE_PASSWORD")
print("here is pass: " + sample_pass)
print(len(sample_pass))
print("None below:")
print(None)
print("type is: " + str(type(sample_pass)))
print("If pass equals None, below:")
print(sample_pass == None)

print("Hello from Docker!")

response = requests.get('https://api.github.com')
print(f"GitHub API status: {response.status_code}")

data = {'Name': ['Alice', 'Bob'], 'Age': [25, 30]}
df = pd.DataFrame(data)
print(df) 

# - docker tag myapp:latest shithi30/myapp:latest # tag before push (ensure login first)
# - docker push shithi30/myapp:latest # push