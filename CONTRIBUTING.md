# Contributing to Chatbot Dynamic Memory System

First off, thank you for considering contributing to this project! 

This document provides guidelines for contributing to the Chatbot Dynamic Memory System. Following these guidelines helps maintain code quality and makes the review process smoother for everyone.

##  Ways to Contribute

There are many ways you can contribute to this project:

- ** Bug Reports**: Find and report bugs with detailed reproduction steps
- ** Feature Requests**: Suggest new features or improvements
- ** Documentation**: Improve or expand documentation
- ** Code Contributions**: Implement features, fix bugs, or optimize performance
- ** Testing**: Add test coverage or improve existing tests
- ** Discussions**: Share ideas, use cases, or help others

##  Getting Started

### Development Setup

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/your-username/chatbot-dynamic-memory.git
   cd chatbot-dynamic-memory
   ```

3. **Create a development branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

4. **Install dependencies**:
   ```bash
   uv sync
   ```

5. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

6. **Install development dependencies**:
   ```bash
   uv sync --extra dev
   ```

### Development Workflow

1. **Make your changes** in your feature branch
2. **Test your changes** locally
3. **Format your code** with Black:
   ```bash
   uv run black src/
   ```
4. **Commit your changes** using conventional commits (see below)
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request** on GitHub

##  Commit Message Guidelines

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear and structured commit messages.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```bash
feat(memory): add conversation summarization
fix(redis): resolve connection pool exhaustion
docs(readme): update installation instructions
refactor(synthesis): simplify context merging logic
perf(qdrant): optimize vector search queries
test(memory): add unit tests for window provider
```

##  Pull Request Process

1. **Update Documentation**: If you change functionality, update relevant docs
2. **Add Tests**: New features should include tests
3. **Follow Code Style**: Run Black formatter before committing
4. **Write Clear Descriptions**: Explain what, why, and how in your PR
5. **Link Issues**: Reference related issues (e.g., "Closes #42")
6. **Keep PRs Focused**: One feature/fix per PR when possible
7. **Be Responsive**: Address review feedback promptly

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How you tested the changes

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-reviewed the code
- [ ] Added/updated documentation
- [ ] Added/updated tests
- [ ] All tests pass locally
```

##  Testing Guidelines

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src tests/

# Run specific test file
uv run pytest tests/test_memory.py
```

### Writing Tests

- Use `pytest` for test framework
- Use `pytest-asyncio` for async tests
- Aim for >80% code coverage
- Test edge cases and error scenarios
- Use fixtures for common setup

Example:
```python
import pytest
from uuid import uuid4

@pytest.mark.asyncio
async def test_memory_window_retrieval():
    user_id = uuid4()
    # Test implementation...
    assert result is not None
```

##  Code Style Guidelines

We use **Black** for code formatting with the following configuration:
- Line length: 88 characters
- Python version: 3.13

### Best Practices

- **Type Hints**: Use type hints for function arguments and returns
- **Docstrings**: Write clear docstrings for public functions/classes
- **Error Handling**: Handle exceptions appropriately
- **Async/Await**: Use async patterns for I/O operations
- **Comments**: Explain "why", not "what" (code should be self-explanatory)

### Example

```python
async def get_context(
    query: str,
    user_id: UUID,
    max_tokens: int = 3000
) -> list[Message]:
    """
    Retrieve relevant context for a query.
    
    Combines recent window messages with semantically similar
    historical messages, respecting token budget constraints.
    
    Args:
        query: User's current query
        user_id: Unique identifier for user isolation
        max_tokens: Maximum tokens for synthesized context
        
    Returns:
        List of messages forming the relevant context
        
    Raises:
        MemoryRetrievalError: If retrieval fails
    """
    # Implementation...
```

##  Bug Reports

When reporting bugs, please include:

### Required Information

1. **Description**: Clear description of the bug
2. **Reproduction Steps**: Minimal steps to reproduce
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   - Python version
   - OS and version
   - Package versions (uv.lock or pip freeze)
6. **Logs/Errors**: Relevant error messages or stack traces

### Bug Report Template

```markdown
**Description**
Brief description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. ...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- Python: 3.13
- OS: macOS 14.0
- Relevant packages: [list versions]

**Additional Context**
Logs, screenshots, etc.
```

##  Feature Requests

When proposing features, please provide:

1. **Use Case**: What problem does this solve?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other approaches you considered
4. **Additional Context**: Examples, mockups, references

### Feature Request Template

```markdown
**Problem/Use Case**
Describe the problem or use case

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
What other approaches did you think about?

**Additional Context**
Any other relevant information
```

##  Priority Areas for Contribution

Looking to contribute but not sure where to start? Here are some areas we'd love help with:

### High Priority

- [ ] **Memory Summarization**: Implement conversation summarization for long contexts
- [ ] **Testing**: Increase test coverage (currently low)
- [ ] **Performance**: Optimize embedding generation and caching
- [ ] **Documentation**: Add more examples and tutorials

### Medium Priority

- [ ] **Memory Decay**: Implement forgetting mechanisms
- [ ] **Multi-modal**: Support for images and files in memory
- [ ] **Analytics**: Usage metrics and monitoring
- [ ] **CLI Tool**: Command-line interface for testing

### Good First Issues

Issues labeled `good first issue` are great for newcomers:
- Documentation improvements
- Simple bug fixes
- Adding examples
- Writing tests

##  Resources

- [Project Documentation](docs/architecture.md)
- [Pydantic AI Docs](https://ai.pydantic.dev)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Redis Documentation](https://redis.io/docs/)

##  Code of Conduct

### Our Standards

- **Be Respectful**: Treat everyone with respect
- **Be Collaborative**: Work together constructively
- **Be Patient**: Help others learn and grow
- **Be Open**: Welcome diverse perspectives

### Unacceptable Behavior

- Harassment or discrimination of any kind
- Trolling, insulting, or derogatory comments
- Public or private harassment
- Publishing others' private information

### Enforcement

Violations can be reported to the project maintainer. All reports will be reviewed and investigated promptly and fairly.

##  Questions?

If you have questions about contributing:

1. Check existing issues and discussions
2. Search the documentation
3. Open a new discussion on GitHub
4. Tag your issue with `question` label

##  Recognition

Contributors will be recognized in:
- Project README
- Release notes
- GitHub contributors page

Thank you for making this project better! 
