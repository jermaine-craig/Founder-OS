# Contributing to Founder OS

Thanks for wanting to contribute. Here is how to add new capabilities.

## Architecture

Founder OS has two layers:

- **Tools** (`tools/`): Python scripts that perform deterministic operations via APIs. They handle auth, make API calls, and return structured data.
- **Skills** (`.claude/skills/`): Markdown instructions that tell Claude when and how to use the tools. Skills are workflows, not code.

## Adding a New Tool

### 1. Create the tool file

Create `tools/yourtool.py` following this pattern:

```python
#!/usr/bin/env python3
"""
Your Tool API for Founder OS.
Brief description of what it does.
"""

import json
import argparse

from tools.auth import get_service  # if using Google APIs
from tools.config import OUTPUT_DIR, TEMP_DIR


def your_function(arg1, arg2=None):
    """
    What this function does.

    Args:
        arg1: Description.
        arg2: Description (optional).

    Returns:
        What it returns.
    """
    # Your implementation
    pass


def main():
    parser = argparse.ArgumentParser(description='Your Tool for Founder OS')
    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Add subcommands
    sub = subparsers.add_parser('your-command', help='What it does')
    sub.add_argument('--arg', required=True, help='Description')

    args = parser.parse_args()

    if args.command == 'your-command':
        your_function(args.arg)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
```

### 2. Add scopes (if using Google APIs)

If your tool needs new Google API scopes, add them to `ALL_SCOPES` in `tools/auth.py`. Users will be prompted to re-authenticate when they next run a tool.

### 3. Add tests

Create `tests/test_yourtool.py`:

```python
import pytest
from unittest.mock import patch, MagicMock


@pytest.mark.unit
class TestYourFunction:
    @patch('tools.yourtool.get_service')
    def test_basic_case(self, mock_service):
        mock_service.return_value = MagicMock()
        # Your test
        pass
```

### 4. Document in CLAUDE.md

Add your tool's CLI commands to `.claude/CLAUDE.md` under the Tools section.

## Adding a New Skill

### 1. Create the skill directory

```
.claude/skills/your-skill/SKILL.md
```

### 2. Write the SKILL.md

```yaml
---
name: your-skill
description: One-line description. Include trigger phrases so Claude knows when to use it.
argument-hint: "your-skill do something"
---

# Your Skill Name

## Process

1. First step
   ```bash
   python3 tools/yourtool.py command --arg value
   ```

2. Second step (what Claude should do with the output)

3. Present results to the user

## Rules

- Safety boundary one
- Safety boundary two
```

### 3. Reference any templates

If your skill needs a consistent output format, create a template in `templates/` and reference it from your skill.

## Running Tests

```bash
# Install dev dependencies
pip install pytest

# Run all tests
pytest -v

# Run just unit tests
pytest -v -m unit
```

## Code Style

- British English spelling
- No em dashes or double dashes in text
- Functions should have docstrings with Args/Returns
- Use `from tools.auth import get_service` for Google APIs
- Use `from tools.config import OUTPUT_DIR` for paths
- Keep tools focused: one tool per API/service
