FROM python:3.9-slim
WORKDIR /app
COPY . /app

RUN apt-get update && apt-get install -y \
    build-essential libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# explictly set versions
RUN pip install --upgrade pip
RUN pip install botocore==1.31.17 boto3==1.28.17 cached-path==1.5.0

RUN pip install -e .
RUN python -m unidic download
RUN python melo/init_downloads.py

CMD ["python", "./melo/app.py", "--host", "0.0.0.0", "--port", "8888"]