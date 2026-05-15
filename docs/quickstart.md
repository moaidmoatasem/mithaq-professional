---
title: Quick Start
---

# Quick Start

## Prerequisites

- Docker + Docker Compose
- Ollama installed (`curl -fsSL https://ollama.com/install.sh | sh`)
- Python 3.11+

## Install

```bash
git clone https://github.com/moaidmoatasem/cherenkov-professional.git
cd cherenkov-professional
cp .env.example .env
pip install -e ".[dev]"
```

## Start

```bash
docker-compose -f deploy/docker-compose.yml up -d
ollama pull qwen2.5-coder:3b
```

## First scan

```bash
cherenkov scan https://example.com --output table
```

## Dashboard

Open [http://localhost:8000/app](http://localhost:8000/app)
