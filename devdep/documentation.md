# Developer Department Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Agent Roles](#agent-roles)
4. [Superpowers Methodology](#superpowers-methodology)
5. [MCP Integration](#mcp-integration)
6. [Docker Configuration](#docker-configuration)
7. [Usage Guide](#usage-guide)
8. [Customization](#customization)
9. [Troubleshooting](#troubleshooting)

## Overview

The Developer Department (DevDep) is an autonomous software development team built with Agno agents following the Superpowers methodology. It integrates with MCP servers to extend its knowledge and capabilities, enabling it to develop complete software systems with minimal human intervention.

## Architecture

The system consists of four specialized agents working together as a coordinated team following the Superpowers methodology:

1. **Brainstorming Agent**: Handles requirement analysis and specification creation
2. **Planning Agent**: Designs system architecture and creates implementation plans
3. **TDD Developer**: Implements features following Test-Driven Development principles
4. **Review Agent**: Ensures quality through comprehensive review processes

All agents operate within a Docker container for isolation and security, with persistent storage for generated code and data.

## Agent Roles

### Brainstorming Agent
- Analyzes user requirements and converts them into detailed technical specifications
- Creates and maintains SPEC.md for project specifications
- Implements spec review loops with subagent reviewers
- Uses Context7 MCP to validate technology choices and best practices
- Employs git clone via ShellTools when GitHub MCP is unavailable

### Planning Agent
- Designs system architecture based on approved specifications
- Breaks down projects into manageable tasks in PLAN.md
- Utilizes Context7 MCP for framework-specific best practices
- Selects appropriate technologies and libraries
- Estimates task complexity and duration

### TDD Developer
- Implements features following the TDD cycle (Red → Green → Refactor)
- Writes clean, well-documented code using FastAPI and SQLite
- Uses ShellTools for executing system commands and tests
- Accesses GitHub repositories for reference implementations when needed
- Commits working code with descriptive messages

### Review Agent
- Validates implemented features through comprehensive testing
- Conducts two-stage review process (spec compliance and code quality)
- Ensures test coverage exceeds 90% before approval
- Checks database integrity after test runs
- Provides feedback to developers for improvements

## Superpowers Methodology

The Superpowers methodology enforces disciplined development practices through four key phases:

1. **Brainstorming**: Understand requirements before planning
   - Analyze project context and ask clarifying questions
   - Propose multiple approaches with trade-off analysis
   - Create specification documents with review loops

2. **Planning**: Create detailed implementation plans
   - Break down specifications into small, manageable tasks
   - Organize tasks in sequential order with dependencies
   - Create comprehensive PLAN.md files

3. **TDD Implementation**: Execute tasks with Test-Driven Development
   - Write failing tests first (Red)
   - Implement minimal code to pass tests (Green)
   - Refactor while maintaining passing tests (Refactor)
   - Commit working code with comprehensive tests

4. **Review**: Validate implementation through comprehensive review
   - Stage 1: Spec compliance review
   - Stage 2: Code quality review
   - Provide feedback for improvements

## MCP Integration

### Context7 MCP
- Provides framework documentation and best practices
- No API key required for basic functionality
- Accessed via query-docs tool for technical questions

### GitHub MCP
- Allows reading and analyzing public repositories
- Requires GitHub Personal Access Token for stable API limits
- Falls back to git clone via ShellTools when token is not provided

## Docker Configuration

The Docker setup ensures a consistent, isolated environment:

- Python 3.11 slim base image
- Pre-installed Node.js for MCP server execution
- System tools: git, curl, sqlite3
- Pre-installed MCP servers for faster startup
- Volume mapping for persistent workspace

## Usage Guide

1. **Environment Setup**:
   ```
   cp devdep/.env.example .env
   # Edit .env with your API keys
   ```

2. **Running the System**:
   ```
   docker-compose -f devdep/docker-compose.yml up --build
   ```

3. **Monitoring Progress**:
   - Generated files appear in the `output` directory
   - View agent activities through container logs
   - Monitor test results and implementation progress

4. **Customizing Tasks**:
   - Modify the task in `devdep/main.py`
   - Adjust agent instructions for specific requirements
   - Extend agent capabilities with additional tools

## Customization

### Adding New Agents
Create new agent definitions in `devdep/main.py` following the existing patterns.

### Extending Tools
Add new tools to agents by including them in the tools array of agent definitions.

### Modifying Methodology
Adjust agent instructions to modify the Superpowers methodology implementation.

### Changing Technologies
Update dependencies in pyproject.toml and requirements.txt for different technology stacks.

## Troubleshooting

### Common Issues

1. **MCP Servers Not Starting**:
   - Check internet connectivity
   - Verify Node.js installation in container
   - Confirm API keys in .env file

2. **Agents Not Producing Output**:
   - Check OpenAI API key validity
   - Verify sufficient tokens in account
   - Review agent instructions for clarity

3. **Docker Build Failures**:
   - Ensure Docker daemon is running
   - Check disk space availability
   - Verify file permissions

### Debugging Tips

1. Set AGNO_LOG_LEVEL=DEBUG in .env for detailed logs
2. Use SHOW_TOOL_CALLS=true to see agent tool usage
3. Check container logs with `docker logs agno_superpowers_team`

### Getting Help

For additional support:
- Review the Agno documentation
- Check the Superpowers repository for methodology details
- Consult MCP server documentation for integration specifics