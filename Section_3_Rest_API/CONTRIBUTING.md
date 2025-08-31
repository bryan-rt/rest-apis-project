# Contributing

## How to run the Dockerfile locally

```
docker run -dp 5000:5050 -w /app -v "$(pwd):/app" stores-api sh -c "flask run --host 0.0.0.0"