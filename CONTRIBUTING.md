# Contributing to Constellation Hub

Thank you for your interest in contributing to Constellation Hub! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Issues

1. Check if the issue already exists in [GitHub Issues](https://github.com/TamTunnel/Constellation-Hub/issues)
2. Create a new issue with a descriptive title
3. Include steps to reproduce, expected behavior, and actual behavior
4. Add relevant labels (bug, enhancement, documentation, etc.)

### Submitting Changes

1. **Fork the repository** and create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards:
   - Python: Follow PEP 8, use type hints, run `ruff` for linting
   - TypeScript: Follow ESLint configuration, use strict typing
   - Write tests for new functionality

3. **Run tests** to ensure nothing is broken:
   ```bash
   # Backend
   cd backend/core-orbits && pytest
   
   # Frontend
   cd frontend/web && npm test
   ```

4. **Commit your changes** using conventional commits:
   ```bash
   git commit -m "feat: add satellite coverage visualization"
   git commit -m "fix: correct visibility window calculation"
   git commit -m "docs: update API documentation"
   ```

5. **Push to your fork** and create a Pull Request:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Fill out the PR template** with:
   - Description of changes
   - Related issues
   - Screenshots (for UI changes)
   - Testing performed

### Branch Naming

- `feature/<description>` - New features
- `fix/<description>` - Bug fixes
- `docs/<description>` - Documentation updates
- `chore/<description>` - Maintenance tasks

## Development Setup

See [docs/ops/local_dev.md](docs/ops/local_dev.md) for detailed setup instructions.

### Quick Start

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Constellation-Hub.git
cd Constellation-Hub

# Start with Docker
docker-compose up -d

# Or run services individually for development
cd backend/core-orbits
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Code Style

### Python

- Use Python 3.11+
- Follow PEP 8 style guide
- Use type hints for all function parameters and returns
- Use `ruff` for linting: `ruff check .`
- Write docstrings for public functions and classes

### TypeScript

- Use strict TypeScript mode
- Follow ESLint configuration
- Use functional components with hooks
- Write tests using Vitest

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation change
- `style:` - Code style change (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Testing

- Write unit tests for all new functionality
- Maintain minimum 80% code coverage
- Write integration tests for API endpoints
- Run the full test suite before submitting PRs

## Documentation

- Update README if adding new features
- Document API changes in `/docs/api/`
- Add docstrings to public functions
- Update architecture docs for structural changes

## Questions?

Feel free to open an issue with your question or reach out to the maintainers.

Thank you for contributing! 🚀
