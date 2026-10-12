FROM python:3.11-slim
WORKDIR /app
COPY requirements.lock.txt .
RUN pip install --no-cache-dir -r requirements.lock.txt
COPY packages ./packages
COPY ml ./ml
COPY services ./services
ENV PYTHONPATH=/app
CMD ["uvicorn", "services.api.oncofusion.main:app", "--host", "0.0.0.0", "--port", "8000"]
