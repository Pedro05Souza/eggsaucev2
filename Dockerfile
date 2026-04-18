FROM python:3.12.0-alpine

WORKDIR /app

RUN echo 'http://dl-cdn.alpinelinux.org/alpine/edge/main' >> /etc/apk/repositories \
    && apk update \
    && apk add --no-cache postgresql17-client

COPY pyproject.toml ./

RUN pip install --no-cache-dir uv && uv pip compile pyproject.toml -o requirements.txt && pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]