FROM python:3.10-slim
WORKDIR /app

# Pip install
ADD src ./src
ADD pyproject.toml .
ADD setup.py .

RUN pip install . --no-cache-dir

CMD ["fastapi", "run", "src/aind_metadata_service_server/main.py", "--port", "80"]
