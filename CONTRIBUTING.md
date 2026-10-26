# Contributing to UK Wind Forecast Accuracy Dashboard

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions.

## Getting Started

### Prerequisites
- Node.js 22+ and npm 10+
- Python 3.12+
- Docker 24+
- Git

### Setup
```bash
git clone <repository-url>
cd uk-energy-analytics-dashboard

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Changes
- Write code following style guidelines (see below)
- Add tests for new functionality
- Update documentation if needed

### 3. Test
```bash
# Backend tests
cd backend
pytest -v

# Frontend build
cd frontend
npm run build
```

### 4. Commit
```bash
git add .
git commit -m "feat: add new forecast comparison feature"
```

**Commit Message Format:**
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation only
- `style:` Formatting, no code change
- `refactor:` Code restructuring
- `test:` Adding tests
- `chore:` Maintenance tasks

### 5. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python (Backend)
- **Formatter:** Black (line length 100)
- **Linter:** Ruff
- **Type Hints:** Required for all function signatures
- **Docstrings:** Google style for public functions

```python
def calculate_mae(forecasts: list[float], actuals: list[float]) -> float:
    """Calculate Mean Absolute Error.
    
    Args:
        forecasts: List of forecast values
        actuals: List of actual values
        
    Returns:
        Mean absolute error (float)
    """
    return np.mean(np.abs(np.array(forecasts) - np.array(actuals)))
```

**Run formatters:**
```bash
cd backend
black . --line-length 100
ruff check . --fix
```

### TypeScript (Frontend)
- **Formatter:** Prettier
- **Linter:** ESLint
- **Types:** Explicit types for function parameters and returns

```typescript
interface KPIData {
  mae_mw: number;
  rmse_mw: number;
  bias_mw: number;
}

function formatMetric(value: number, unit: string): string {
  return `${value.toFixed(1)} ${unit}`;
}
```

**Run formatters:**
```bash
cd frontend
npm run lint
npm run format
```

## Testing

### Backend Tests (pytest)
- Unit tests for all services
- Test file naming: `test_<module_name>.py`
- Use fixtures in `conftest.py`

```python
def test_hourly_aggregation(fuelhh_two_half_hours):
    """Test averaging two half-hours into one hourly value."""
    result = aggregate_fuelhh_to_hourly(fuelhh_two_half_hours)
    assert len(result) == 1
    assert result[0].generation_mw == 14456.5
```

### Frontend Tests (Vitest)
- Component tests with React Testing Library
- Test file naming: `<ComponentName>.test.tsx`

```typescript
describe('KPICard', () => {
  it('renders label and value', () => {
    render(<KPICard label="MAE" value={892.5} unit="MW" />);
    expect(screen.getByText('MAE')).toBeInTheDocument();
    expect(screen.getByText('892.5 MW')).toBeInTheDocument();
  });
});
```

## Pull Request Guidelines

### PR Title
Use same format as commit messages:
```
feat: add date range filter to time series chart
```

### PR Description Template
```markdown
## Summary
Brief description of changes.

## Changes
- Bullet list of specific changes
- Include files modified

## Testing
- [ ] Backend tests pass (pytest)
- [ ] Frontend builds (npm run build)
- [ ] Manual testing performed
- [ ] Documentation updated

## Screenshots (if UI changes)
[Attach screenshots]
```

### Review Process
1. Automated checks run (linting, tests)
2. Code review by maintainer
3. Address feedback
4. Merge once approved

## Documentation

### When to Update Docs
- New API endpoints → Update `docs/API.md`
- New metrics → Update `docs/FORECAST_METHODOLOGY.md`
- UI changes → Update `docs/USER_GUIDE.md`
- Architecture changes → Update `docs/ARCHITECTURE.md`

### Markdown Style
- Use ATX headers (`# Heading`)
- Code blocks with language tags
- Tables for structured data
- Links to related docs

## Release Process

1. Update version in `package.json` and `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release tag: `git tag v1.1.0`
4. Push tag: `git push --tags`
5. Create GitHub Release with notes

## Questions?

- Check [USER_GUIDE.md](docs/USER_GUIDE.md) for usage
- Check [ARCHITECTURE.md](docs/ARCHITECTURE.md) for design
- Open a GitHub Issue for bugs or feature requests

## License

[Specify license, e.g., MIT]

---

**Thank you for contributing!**
