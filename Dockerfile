FROM python:3.11-alpine

WORKDIR /app

# Docker CLI (for container log watching)
RUN apk add --no-cache docker-cli

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ ./src/

# Run
CMD ["python", "-m", "src.main"]
