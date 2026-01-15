#!/bin/bash
# Start Simple HTTP Server for Preview UI

echo "🌐 Starting Preview Server..."
echo ""
echo "   URL: http://localhost:8000"
echo "   File: preview_ui.html"
echo ""
echo "กด Ctrl+C เพื่อหยุด server"
echo ""

cd /Users/fastwork/Desktop/form
python3 -m http.server 8000
