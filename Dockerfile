FROM python:3.8.6

WORKDIR /app

RUN apt-get update && apt-get install -y netcat

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./entrypoint.dev.sh .
RUN chmod +x /app/entrypoint.dev.sh

COPY . .

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.dev.sh"]
