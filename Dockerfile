FROM python:3.10

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir selenium beautifulsoup4 requests google-cloud-storage python-dotenv

RUN apt-get update && apt-get install -y wget unzip && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean

CMD ["python", "Blob Store Banners.py"]