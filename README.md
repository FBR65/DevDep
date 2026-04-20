# Developer Department (DevDep)

An autonomous software development team powered by Agno agents following the Superpowers methodology, integrated with MCP servers for enhanced capabilities.

## Overview

This project implements a complete developer department setup using:
- **Agno agents** for orchestration
- **Superpowers methodology** for disciplined development practices
- **MCP integration** with Context7 and GitHub for extended knowledge
- **Docker containers** for isolated development environments
- **uv package manager** for fast dependency management
- **SQLite database** for lightweight data persistence

## Features

1. **Multi-Agent Team Structure**:
   - Brainstorming Agent: Requirement analysis and specification creation
   - Planning Agent: System architecture and planning
   - TDD Developer: Test-driven development implementation
   - Review Agent: Testing and quality assurance

2. **Superpowers Methodology Integration**:
   - Brainstorming phase for requirement understanding
   - Planning phase with detailed task breakdown
   - Test-Driven Development (TDD) implementation with Red-Green-Refactor cycle
   - Two-stage review process (spec compliance and code quality)

3. **MCP Server Integration**:
   - Context7 for framework documentation and best practices
   - GitHub MCP for code reference and repository analysis

4. **Dockerized Environment**:
   - Isolated development environment
   - Persistent workspace through volume mapping
   - Pre-installed tools and dependencies

## Project Structure

```
devdep/
├── main.py              # Main application with agent definitions
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── .env.example         # Example environment variables
├── agents/              # Custom agent implementations
├── tools/               # Custom tool implementations
├── mcp/                 # MCP server configurations
├── services/            # Service integrations
└── workspace/           # Workspace for generated files
```

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd devdep
   ```

2. **Install uv package manager**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Copy and configure environment variables**:
   ```bash
   cp devdep/.env.example .env
   # Edit .env file with your actual API keys
   ```

4. **Build and run with Docker Compose**:
   ```bash
   docker-compose -f devdep/docker-compose.yml up --build
   ```

## Usage

Once the system is running, the agent team will automatically start working on the example task defined in `main.py`. You can modify this task or provide your own instructions.

The generated code and files will be available in the `output` directory on your host machine.

## Customization

You can customize the agent behaviors by modifying:
- `devdep/main.py`: Agent definitions and team orchestration
- `devdep/.env.example`: Environment variables template
- `devdep/Dockerfile`: Docker image configuration
- `devdep/docker-compose.yml`: Container orchestration

## Requirements

- Docker and Docker Compose
- OpenAI API key
- (Optional) GitHub Personal Access Token for extended GitHub access

## License

This project is licensed under the MIT License - see the LICENSE file for details.