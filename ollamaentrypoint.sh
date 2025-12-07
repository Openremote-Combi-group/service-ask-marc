#!/bin/bash
set -e

ollama serve &
SERVER_PID=$!
sleep 10

# Pull TOOL-SUPPORTING model instead of base llama3
echo "Pulling llama3.1 (tool support)..."
ollama pull llama3.1:8b  # or llama3.1:70b if VRAM allows

echo "Ollama ready with llama3.1 (tools enabled)!"
wait $SERVER_PID
