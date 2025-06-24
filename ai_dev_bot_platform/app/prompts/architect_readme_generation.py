# app/prompts/architect_readme_generation.py

PROMPT = """
You are an expert technical writer. Generate a comprehensive README.md for the project titled '{project_title}'.
Include these REQUIRED sections with appropriate content:

## Table of Contents
- Quick navigation links to all sections

## Overview
- Brief description of the project
- Key features and capabilities
- Project status/version

## Setup
### Development
- System requirements
- Installation from source
- Setting up development environment
- Dependencies: {dependencies}

### Production
- Package manager installation
- Container deployment (Docker)
- One-line install commands

## Configuration
- Environment variables: {env_vars}
- Configuration files and their locations
- Security best practices

## Usage
- How to run the application
- Command line options/flags
- Examples of common use cases with code samples
- API documentation if applicable

## Deployment
- Containerization (Docker)
- Kubernetes manifests
- Cloud deployment (AWS/GCP/Azure)
- Scaling considerations

## Contributing
- How to submit issues
- Pull request workflow
- Coding standards
- Testing requirements

## Tests
- How to run the test suite
- Coverage reporting
- Writing new tests

## Support
- How to get help
- Community forums
- Commercial support options

## License
- License type (e.g., MIT, Apache)
- Copyright notice

## Acknowledgments
- Third-party libraries
- Inspiration/credits
- Team members

Project Description:
{project_description}

Technical Documentation:
{documentation}

Use proper Markdown formatting with:
- Clear section headers
- Consistent indentation
- Code blocks for commands
- Tables where appropriate
- Badges for build status/version (if available)
- Actual values from project context (no placeholders)
"""