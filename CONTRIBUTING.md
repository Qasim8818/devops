# Contributing Guide

Contribute to the DevSecOps Agent project.

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Code Standards](#code-standards)
5. [Testing](#testing)
6. [Commit Guidelines](#commit-guidelines)
7. [Pull Request Process](#pull-request-process)
8. [Reporting Bugs](#reporting-bugs)
9. [Feature Requests](#feature-requests)

---

## Code of Conduct

- Be respectful of others
- Report issues privately if they involve security
- Help other contributors
- Assume good intent

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node 18+
- Docker & Docker Compose
- Git

### Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/devsecops-agent.git
cd devsecops-agent
git remote add upstream https://github.com/original/devsecops-agent.git
```

---

## Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# Run tests
pytest --cov=.

# Start backend (standalone)
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm start

# Runs at http://localhost:3000
```

### Full Stack Local

```bash
docker compose -f docker-compose.dev.yml up
```

---

## Code Standards

### Python
- Use Black for formatting
- Follow PEP 8
- Type hints required
- Docstrings for all functions

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type check
mypy backend/
```

### JavaScript/React
- Use Prettier for formatting
- Follow ESLint rules
- Functional components
- Meaningful component names

```bash
cd frontend
npm run lint
npm run format
```

### Naming Conventions
- Python: `snake_case` for functions/variables
- Python: `PascalCase` for classes
- JavaScript: `camelCase` for functions/variables
- JavaScript: `PascalCase` for components

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_monitoring.py

# Run specific test
pytest tests/test_monitoring.py::test_anomaly_detection
```

### Test Structure
```python
def test_feature_success():
    """Test successful feature behavior"""
    # Arrange
    input_data = ...
    
    # Act
    result = function(input_data)
    
    # Assert
    assert result == expected
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Coverage
npm test -- --coverage
```

### Integration Tests

```bash
docker compose -f docker-compose.test.yml up
docker compose exec backend pytest tests/integration/
```

---

## Commit Guidelines

### Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style (formatting)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Test improvements
- `chore`: Build/deps/config

### Examples
```
feat(monitoring): add memory anomaly detection

Add memory usage threshold checking and alerting.
Includes unit tests and documentation.

Closes #123
```

```
fix(api): handle null values in incident response

Prevent null pointer exceptions when incident.description is missing.

Fixes #456
```

```
docs(setup): add Slack integration guide

Add step-by-step instructions for configuring Slack webhooks.
```

### Commit Checklist
- [ ] Tests pass locally
- [ ] Code formatted (Black/Prettier)
- [ ] Docstrings/comments added
- [ ] No debug code left in
- [ ] No large files committed
- [ ] Updated relevant documentation

---

## Pull Request Process

### Before Creating PR
1. Update your branch from `main`
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. Create feature branch
   ```bash
   git checkout -b feature/my-feature
   ```

3. Make changes and commit
   ```bash
   git add .
   git commit -m "feat(module): description"
   ```

4. Push to your fork
   ```bash
   git push origin feature/my-feature
   ```

### Create PR
1. Go to your fork on GitHub
2. Click "Create Pull Request"
3. Fill out the template completely
4. Link related issues: `Closes #123`

### PR Template
```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing completed

## Screenshots (if applicable)
```

### PR Review Process
- **Automated checks** must pass (CI/CD)
- **At least 1 approval** required
- **Conversations resolved**
- **Branch up to date** with main

### Merging
- Squash commits for small PRs
- Keep history for major features
- Delete branch after merge

---

## Reporting Bugs

### Security Issues
🚨 **DO NOT** open public GitHub issues for security vulnerabilities.

Email: security@devsecops.local

### Regular Bugs

1. Check existing issues first
2. Create issue with template
3. Include:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots/logs
   - System info

### Bug Report Template
```markdown
## Description
Clear description of the bug.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Logs/Error Messages
```
Error message here
```

## Environment
- OS: [e.g. Ubuntu 20.04]
- Docker version: [e.g. 20.10.5]
- Python version: [if applicable]
```

---

## Feature Requests

### Evaluation Criteria
- Aligns with project goals
- Not in conflict with other features
- Feasible to implement
- Value to users

### Request Template
```markdown
## Feature
Clear title and description.

## Problem
What problem does this solve?

## Solution
How should it work?

## Alternatives
Other approaches considered?

## Additional Context
Links, references, use cases?
```

---

## Development Tips

### Debug Backend
```python
import pdb; pdb.set_trace()

# or use ipdb for better interface
import ipdb; ipdb.set_trace()
```

### Debug Frontend
```javascript
console.log('debug info', variable);
debugger;  // Pauses execution in DevTools
```

### Performance Profiling
```python
# Backend
python -m cProfile -s cumtime main.py

# Frontend
npm run build -- --analyze
```

### Git Tips
```bash
# See what changed
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Interactive rebase
git rebase -i HEAD~3

# Stash changes temporarily
git stash
git stash pop
```

---

## Resources

- [Project Board](https://github.com/yourname/devsecops-agent/projects)
- [Discussions](https://github.com/yourname/devsecops-agent/discussions)
- [Python Style Guide](https://pep8.org/)
- [JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html)

---

## Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](CONTRIBUTORS.md)
- GitHub contributor graph
- Release notes

---

Thank you for contributing! 🙏
