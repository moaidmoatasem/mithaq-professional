#!/bin/bash

watch -n 2 '
clear
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  📊 mithaq PERFECTION - LIVE MONITORING                      ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Container Status:"
docker-compose -f docker-compose.optimized.yml ps
echo ""
echo "Resource Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
echo ""
echo "Recent Logs:"
docker-compose -f docker-compose.optimized.yml logs --tail=5
echo ""
echo "Press Ctrl+C to exit monitoring"
'

