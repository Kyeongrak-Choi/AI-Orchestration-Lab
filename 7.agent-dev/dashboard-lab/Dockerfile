# Day 6에서 만든 이미지 정의 (Day 8 CI가 이 파일로 빌드를 검증한다)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Docker가 주기적으로 /health를 확인한다 (우리 watchdog의 is_healthy와 같은 역할)
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c "import httpx; exit(0 if httpx.get('http://127.0.0.1:8000/health').status_code == 200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]