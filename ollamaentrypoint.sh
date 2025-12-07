#!/bin/bash
set -e

ollama serve &
SERVER_PID=$!

echo "Waiting for Ollama server..."
sleep 10

echo "Pulling llama3..."
ollama pull llama3

echo "Ollama ready with llama3 loaded!"
wait $SERVER_PID
