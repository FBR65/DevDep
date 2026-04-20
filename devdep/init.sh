#!/bin/bash

# Developer Department Initialization Script

echo "=== Developer Department Setup ==="

# Check if Docker is installed
if ! command -v docker &> /dev/null
then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null
then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null
then
    echo "Warning: uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create output directory if it doesn't exist
mkdir -p output

# Copy .env.example to .env if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp devdep/.env.example .env
    echo "Please edit .env with your actual API keys"
else
    echo ".env file already exists"
fi

echo ""
echo "Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your actual API keys"
echo "2. Run 'docker-compose -f devdep/docker-compose.yml up --build' to start the system"
echo "3. Check the output directory for generated files"