#!/bin/bash

# Pull latest changes
git pull

# Build and restart containers
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up --build -d

# Show logs
docker-compose -f docker-compose.prod.yml logs -f 