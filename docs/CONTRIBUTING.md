# Contributing to PreOffice

Thank you for your interest in contributing to PreOffice!

## Ways to Contribute

- **Report bugs**: Open an issue with reproduction steps
- **Suggest features**: Open a discussion or issue
- **Submit code**: Fork, branch, and open a pull request
- **Improve docs**: Documentation PRs are always welcome
- **Translate**: Help localize PreOffice

## Development Setup

1. Follow [BUILDING.md](BUILDING.md) to set up your environment
2. Create a feature branch from `preoffice/main`
3. Make your changes
4. Run tests: `make check`
5. Submit a pull request

## Code Guidelines

### General
- Follow existing code style in the file you're editing
- Keep changes focused and atomic
- Write clear commit messages

### Commit Messages
```
component: Short description (50 chars max)

Longer explanation if needed. Wrap at 72 characters.
Explain the "why" not just the "what".

Fixes #123
```

### Presearch Integrations
When working in `presearch/integrations/`:
- Keep dependencies minimal
- Support offline/air-gapped mode
- Make endpoints configurable
- Add unit tests

### Core LibreOffice Changes
When modifying `core/`:
- Minimize changes to reduce rebase conflicts
- Document changes in commit message
- Consider if this could be an extension instead
- Add `[PREOFFICE]` tag to changed lines as comment

## Pull Request Process

1. **Title**: Clear, concise description
2. **Description**: What changed and why
3. **Testing**: Describe how you tested
4. **Screenshots**: For UI changes

### Review Criteria
- Code quality and style
- Test coverage
- Documentation updated
- No regressions
- Licensing compliance

## Licensing

- Core fork code: MPL 2.0 (inherited from LibreOffice)
- Presearch integrations: MIT
- Brand assets: Presearch proprietary (not for redistribution)

By contributing, you agree that your contributions will be licensed under the appropriate license for that component.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Assume good intentions
- No harassment or discrimination

## Getting Help

- **Discord**: [Presearch Discord](https://discord.gg/presearch)
- **Issues**: GitHub Issues for bugs/features
- **Discussions**: GitHub Discussions for questions

## Recognition

Contributors are recognized in:
- Git history
- CONTRIBUTORS.md file
- Release notes (for significant contributions)
