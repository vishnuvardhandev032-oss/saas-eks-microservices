FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000
ENV SERVICE_NAME=gateway-api
# these will be overridden by docker-compose / k8s env vars
ENV USERS_BASE_URL=http://users-service:8000
ENV BILLING_BASE_URL=http://billing-service:8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
