#!/bin/bash
set -euo pipefail
echo "CHERENKOV Proving Ground initializing..."

# 1. Dependencies
pip install --upgrade pip
pip install -e ".[dev]"
pip install ollama sentence-transformers qdrant-client websockets
export PYTHONPATH=$PYTHONPATH:$(pwd)/packages:/usr/lib/python3/dist-packages

# 2. Docker + VFS
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
sudo mkdir -p /etc/docker
echo '{"storage-driver":"vfs"}' | sudo tee /etc/docker/daemon.json
sudo systemctl restart docker && sleep 5

# 3. LATTICE
sudo docker run -d --name qdrant --restart unless-stopped \
  -p 6333:6333 qdrant/qdrant

# 4. DVWA (GHCR mirror — avoids Docker Hub rate limit)
sudo docker run -d --name dvwa --restart unless-stopped \
  -p 80:80 \
  ghcr.io/digininja/dvwa:latest

# 5. WebGoat
sudo docker run -d --name webgoat --restart unless-stopped \
  -p 8090:8080 \
  webgoat/webgoat:latest

# 6. Ollama + KINETIC
curl -fsSL https://ollama.com/install.sh | sh
ollama serve > /dev/null 2>&1 &
sleep 8
ollama pull llama3.2:3b

# 7. FE build
[ -f "packages/cherenkov/web/package.json" ] && \
  cd packages/cherenkov/web && npm install && npm run build && cd /app

# 8. Health check
echo "--- Health ---"
sudo docker ps --format "table {{.Names}}\t{{.Status}}"
curl -sf http://localhost:6333/health   && echo " LATTICE  OK" || echo " LATTICE  FAIL"
curl -sf http://localhost:80            > /dev/null \
                                        && echo " DVWA     OK" || echo " DVWA     FAIL"
curl -sf http://localhost:8090          > /dev/null \
                                        && echo " WebGoat  OK" || echo " WebGoat  FAIL"
curl -sf http://localhost:11434/api/tags > /dev/null \
                                        && echo " Ollama   OK" || echo " Ollama   FAIL"
python -c "from cherenkov.core.base_scanner import BaseScanner; print(' Package  OK')"

echo ""
echo "Proving Ground ready."
echo "  DVWA    → http://localhost:80     (admin/password after setup.php)"
echo "  WebGoat → http://localhost:8090"
echo "  LATTICE → http://localhost:6333"
echo "  Ollama  → http://localhost:11434"
