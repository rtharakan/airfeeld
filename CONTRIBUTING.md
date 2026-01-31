# Contributing to Airfeeld

Thank you for your interest in contributing to Airfeeld. This document provides guidelines for contributing to the project.

## Code of Conduct

This project is built for learning, fun, and public interest. We expect all contributors to:

- Be respectful and constructive
- Focus on technical merit
- Maintain privacy and accessibility standards
- Avoid commercial interests or surveillance capabilities

## How to Contribute

### Reporting Issues

Before creating an issue:

1. Check existing issues to avoid duplicates
2. Provide clear reproduction steps
3. Include relevant system information
4. Describe expected vs actual behavior

### Contributing Code

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Follow the specification-driven development workflow**:
   - Read the relevant specification in `specs/001-aviation-games/`
   - Write tests first (TDD)
   - Implement minimum code to pass tests
   - Refactor for clarity and simplicity
4. **Commit with spec references**: `feat(gameplay): implement 3-attempt scoring [spec:001-aviation-games:FR-005]`
5. **Push to your fork**: `git push origin feature/your-feature-name`
6. **Open a pull request**

### Development Setup

See [README.md](README.md#getting-started) for initial setup.

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
cd frontend
npm run test:e2e
```

### Code Style

**Python:**
- Follow PEP 8
- Use `black` for formatting
- Use `ruff` for linting
- Add docstrings to all public functions

**TypeScript:**
- Follow ESLint configuration
- Use Prettier for formatting
- Add JSDoc comments to components
- Use semantic HTML

### Constitution Compliance

All contributions must align with the [Airfeeld Constitution](.specify/memory/constitution.md):

1. **Privacy by Design**: No tracking, minimal data collection
2. **Public Interest First**: Non-commercial, accessible to all
3. **Accessibility as Constraint**: WCAG AA compliance required
4. **Radical Simplicity**: Minimal dependencies, YAGNI principle
5. **Openness in Practice**: Open source, open data, documented decisions
6. **Specification-Driven Development**: Tests before implementation

Contributions that violate these principles will not be accepted.

## Contributing Photos

### Photo Requirements

- Taken during take-off or landing
- Shows identifiable airport features
- Formats: JPEG, PNG, WebP
- Minimum resolution: 800x600px
- Maximum file size: 10MB
- License: Creative Commons (CC BY 2.0 or CC0) or public domain

### Bulk Photo Contributions

For bulk contributions (10+ photos), see [docs/photo-curation.md](docs/photo-curation.md).

## Contributing Aviation Data

Aviation data improvements are welcome:

- Airport corrections (from OurAirports)
- Airline updates (from OpenFlights)
- Aircraft model additions

Submit data changes with references to authoritative sources.

## Documentation

Documentation improvements are always appreciated:

- Fix typos or clarify instructions
- Add examples or tutorials
- Improve accessibility documentation
- Translate to other languages (future)

## Pull Request Guidelines

### Before Submitting

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Commits reference specifications
- [ ] Documentation updated if needed
- [ ] WCAG AA compliance verified for UI changes
- [ ] Privacy audit passed (no tracking added)

### PR Description

Include:

1. **What**: Brief description of changes
2. **Why**: Problem solved or feature added
3. **How**: Technical approach taken
4. **Spec Reference**: Link to relevant spec/requirement
5. **Testing**: How changes were tested
6. **Screenshots**: For UI changes

### Review Process

1. Automated tests run on PR
2. Code review by maintainer
3. Constitution compliance check
4. Accessibility review (for UI changes)
5. Privacy audit (for data-handling changes)

## Architecture Decision Records

For significant architectural decisions, create an ADR in `docs/architecture/`:

```markdown
# ADR-XXX: Decision Title

**Status**: Proposed | Accepted | Deprecated  
**Date**: YYYY-MM-DD  
**Context**: What problem are we solving?  
**Decision**: What did we decide?  
**Consequences**: What are the trade-offs?  
**Constitution Check**: How does this align with principles?
```

## Questions?

Open a discussion on GitHub or comment on relevant issues.

---

**Remember**: Airfeeld is built for learning and public interest, not profit or surveillance. Every contribution should honor this mission.
