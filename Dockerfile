#FROM ubuntu:20.04
#FROM selenium/standalone-chrome
FROM python:3.10

WORKDIR /resy_app/

RUN apt update
RUN apt-get install -y libnss3 libgconf-2-4 chromium-driver
COPY . .
RUN python -m pip install -r requirements.txt

# RUN apt-get update && apt-get install -y python3.10 python3.10-dev

# COPY requirements.txt .

# RUN pip install -r requirements.txt
CMD ["python", "web.py", "--type", "headless"]