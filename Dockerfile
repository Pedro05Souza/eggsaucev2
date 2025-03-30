FROM python:3.12.0-alpine AS builder

WORKDIR /app

COPY requirements.txt .

COPY . .

FROM python:3.12.0-alpine

WORKDIR /app

RUN echo 'http://dl-cdn.alpinelinux.org/alpine/edge/main' >> /etc/apk/repositories \
    && apk update \
    && apk add --no-cache postgresql17-client

COPY --from=builder /app /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]