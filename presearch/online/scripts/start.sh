#!/bin/bash
# PreOffice Online - Startup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║              PreOffice Online - Startup                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}[WARN]${NC} .env file not found. Creating from example..."
    cp .env.example .env
    echo -e "${YELLOW}[WARN]${NC} Please edit .env with your configuration before production use."
fi

# Check for SSL certificates
if [ ! -f nginx/ssl/fullchain.pem ]; then
    echo -e "${YELLOW}[WARN]${NC} SSL certificates not found."
    echo "For development, generating self-signed certificates..."
    mkdir -p nginx/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/privkey.pem \
        -out nginx/ssl/fullchain.pem \
        -subj "/CN=localhost" 2>/dev/null
    echo -e "${GREEN}[OK]${NC} Self-signed certificates generated."
    echo -e "${YELLOW}[NOTE]${NC} For production, use Let's Encrypt or your own certificates."
fi

# Build WOPI server
echo -e "${BLUE}[INFO]${NC} Building WOPI server..."
docker compose build wopi

# Start services
echo -e "${BLUE}[INFO]${NC} Starting PreOffice Online services..."
docker compose up -d

# Wait for services to be ready
echo -e "${BLUE}[INFO]${NC} Waiting for services to start..."
sleep 10

# Health check
echo -e "${BLUE}[INFO]${NC} Checking service health..."

if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} WOPI server is running"
else
    echo -e "${YELLOW}[WARN]${NC} WOPI server may still be starting..."
fi

if curl -s http://localhost:9980/hosting/discovery > /dev/null 2>&1; then
    echo -e "${GREEN}[OK]${NC} Collabora Online is running"
else
    echo -e "${YELLOW}[WARN]${NC} Collabora Online may still be starting..."
fi

echo ""
echo -e "${GREEN}PreOffice Online is starting!${NC}"
echo ""
echo "Services:"
echo "  - Web UI:      https://localhost (or your domain)"
echo "  - WOPI Server: http://localhost:8080"
echo "  - Collabora:   http://localhost:9980"
echo ""
echo "Commands:"
echo "  - View logs:   docker compose logs -f"
echo "  - Stop:        docker compose down"
echo "  - Restart:     docker compose restart"
echo ""
