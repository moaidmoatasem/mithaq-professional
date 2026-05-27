#!/bin/bash
set -euo pipefail

echo "Detecting hardware..."
python3 -c "
import os, sys
sys.path.insert(0, os.path.realpath('packages'))

from cherenkov.ai.model_selector import generate_litellm_config, recommend_models

recs = recommend_models()
hw = recs['hardware']
print(f\"RAM: {hw['ram_gb']}GB | GPU: {hw['gpu_name']} {hw['vram_gb']}GB | Tier: {hw['tier']}\")
print()
print('Recommended models:')
for role, info in recs['selected'].items():
    print(f\"  {role:12} -> {info['model']:40} ({info['size_gb']}GB)\")
print()
print('Pull commands:')
for cmd in recs['pull_commands']:
    print(f\"  {cmd}\")
print()
print('Advice:', recs['advice'])
print()
print('Generating litellm config...')
config = generate_litellm_config(recs)
with open(os.path.expanduser('~/litellm-config.yaml'), 'w') as f:
    f.write(config)
print('Written to ~/litellm-config.yaml')
"
