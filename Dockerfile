FROM python:3.12.0-alpine AS builder

WORKDIR /app

COPY requirements.txt .

COPY . .

FROM python:3.12.0-alpine

WORKDIR /app

COPY --from=builder /app /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]