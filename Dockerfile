FROM python:3.11-slim

WORKDIR /app

COPY main.py ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

ENV GOAT_RPC_NODE=https://rpc.goat.network

CMD ["python", "main.py"]