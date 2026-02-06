#!/bin/bash
# Start Noode Development Environment

set -e

echo "🚀 Starting Noode Development Environment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Starting Docker services...${NC}"
docker-compose up -d qdrant

# Wait for Qdrant to be healthy
echo -e "${YELLOW}⏳ Waiting for Qdrant to be ready...${NC}"
sleep 3

# Check if Qdrant is healthy
if curl -s http://localhost:6333/healthz > /dev/null; then
    echo -e "${GREEN}✅ Qdrant is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Qdrant health check failed, but continuing...${NC}"
fi

echo ""
echo -e "${GREEN}✅ Environment started successfully!${NC}"
echo ""
echo "Available services:"
echo "  - Qdrant:      http://localhost:6333"
echo "  - Noode API:   http://localhost:8000 (start manually with: source .venv/bin/activate && python -m uvicorn noode.api.server:app --reload)"
echo ""
echo "To stop: docker-compose down"
