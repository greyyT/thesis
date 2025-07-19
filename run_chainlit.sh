#!/bin/bash
# Run the Chainlit UI

echo "🚀 Starting AI Recruitment Assistant..."
echo "📍 URL: http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

uv run chainlit run src/main.py --port 8000