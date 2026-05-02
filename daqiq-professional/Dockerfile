FROM python:3.12-slim

LABEL maintainer="DAQIQ Autonomous Agents"
LABEL description="Autonomous agent swarm for security testing"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY daqiq/ ./daqiq/
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY examples/ ./examples/

# Set PYTHONPATH
ENV PYTHONPATH=/app/src:/app

# Create workflow results directory
RUN mkdir -p /app/workflow_results

# Default command - run demo
CMD ["python", "scripts/demo_workflow_execution.py"]
