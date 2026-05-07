#!/bin/bash

case "$1" in
    build)
        echo "🔨 Building Docker images..."
        docker compose build --no-cache
        ;;
    up)
        echo "🚀 Starting all services..."
        docker compose up -d
        ;;
    down)
        echo "🛑 Stopping all services..."
        docker compose down
        ;;
    restart)
        echo "🔄 Restarting services..."
        docker compose restart
        ;;
    logs)
        docker compose logs -f
        ;;
    status)
        echo "📊 Service Status:"
        docker compose ps
        echo ""
        echo "💾 Resource Usage:"
        docker stats --no-stream
        ;;
    clean)
        echo "🧹 Cleaning up..."
        docker compose down -v
        docker system prune -f
        ;;
    *)
        echo "mithaq Docker Manager"
        echo ""
        echo "Usage: $0 {build|up|down|restart|logs|status|clean}"
        echo ""
        echo "Commands:"
        echo "  build   - Build all images"
        echo "  up      - Start all services"
        echo "  down    - Stop all services"
        echo "  restart - Restart services"
        echo "  logs    - View logs"
        echo "  status  - Show status and resources"
        echo "  clean   - Remove all containers and volumes"
        ;;
esac

