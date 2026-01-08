#!/bin/bash
# Docker helper script for cross-platform development
# Supports: Windows (Docker Desktop), Linux (Docker daemon), and dev containers

set -e

show_help() {
    cat << EOF
🐳 Docker Helper Script

This script provides cross-platform Docker support for the MCP Web Search project.

Available commands:
  $0 build     - Build Docker image
  $0 run       - Run Docker container
  $0 compose   - Run with Docker Compose
  $0 down      - Stop Docker Compose services
  $0 help      - Show this help message

Platform-specific setup:

📦 Windows (Docker Desktop):
   1. Install Docker Desktop from: https://docs.docker.com/desktop/install/windows-install/
   2. Ensure Docker Desktop is running
   3. Run: $0 build

🐧 Linux:
   1. Install Docker: sudo apt-get install docker.io docker-compose
   2. Add user to docker group: sudo usermod -aG docker \$USER
   3. Logout and login again (or: newgrp docker)
   4. Run: $0 build

🔷 Dev Container (VS Code):
   - Dev container has Docker CLI but no daemon access by default
   - Use one of the above methods from your host machine
   - Or enable Docker-in-Docker in devcontainer.json

EOF
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed!"
        show_help
        exit 1
    fi

    if ! docker ps &> /dev/null 2>&1; then
        echo "❌ Docker daemon is not accessible"
        echo ""
        echo "Possible fixes:"
        echo "  1. Linux users: sudo usermod -aG docker \$USER && newgrp docker"
        echo "  2. Try: sudo $0 $@"
        echo "  3. Check if Docker Desktop is running (Windows/Mac)"
        echo ""
        show_help
        exit 1
    fi
}

build_image() {
    check_docker
    echo "🔨 Building Docker image..."
    docker build -t mcp-web-search:latest .
    echo "✅ Build complete!"
}

run_container() {
    check_docker
    echo "🚀 Running Docker container..."
    docker run -p 8000:8000 --env-file .env mcp-web-search:latest
}

compose_up() {
    check_docker
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed!"
        echo "Install with: sudo apt-get install docker-compose (Linux)"
        exit 1
    fi
    echo "🚀 Starting Docker Compose services..."
    docker-compose up -d
}

compose_down() {
    check_docker
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed!"
        exit 1
    fi
    echo "🛑 Stopping Docker Compose services..."
    docker-compose down
}

case "${1:-help}" in
    build)
        build_image
        ;;
    run)
        run_container
        ;;
    compose)
        compose_up
        ;;
    down)
        compose_down
        ;;
    help)
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        show_help
        exit 1
        ;;
esac
