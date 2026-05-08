#!/bin/bash
# cherenkov NEXUS - Quick Setup Script

echo "🚀 cherenkov NEXUS - AI Security Orchestrator Setup"
echo "================================================================"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

echo "✅ Docker found"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose not found. Please install it:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker Compose found"
echo ""

# Create results directory
mkdir -p results

# Start all services
echo "🐳 Starting all cherenkov NEXUS services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

# Download AI models
echo ""
echo "📥 Downloading AI models (this may take 5-10 minutes)..."
echo "   Model 1: DeepSeek-R1 1.5B (fast, efficient)..."
docker exec cherenkov-ollama ollama pull deepseek-r1:1.5b

echo "   Model 2: Qwen 2.5 3B (better reasoning)..."
docker exec cherenkov-ollama ollama pull qwen2.5:3b

echo ""
echo "================================================================"
echo "✅ cherenkov NEXUS IS READY!"
echo "================================================================"
echo ""
echo "Services running:"
echo "  🤖 AI Orchestrator:  http://localhost:8000"
echo "  🔍 OWASP ZAP:        http://localhost:8080"
echo "  🧠 Ollama API:       http://localhost:11434"
echo "  📊 Redis:            localhost:6379"
echo ""
echo "📖 Test the API:"
echo "   curl http://localhost:8000/"
echo ""
echo "🔍 Start a scan:"
echo "   curl -X POST http://localhost:8000/api/scan \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"target\": \"https://example.com\", \"scan_types\": [\"web\", \"ai-agent\"]}'"
echo ""
echo "View logs:     docker-compose logs -f orchestrator"
echo "Stop services: docker-compose down"
echo ""
echo "================================================================"

