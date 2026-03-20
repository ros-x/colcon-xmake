---
sidebar_position: 3
title: Release
---

# colcon-xmake Release Notes Process

1. Update version in:
- `setup.cfg`
- `colcon_xmake/__init__.py`

2. Run checks:
- `python3 -m pytest -q`
- workspace E2E scripts from root repo

3. Tag release:
- `git tag vX.Y.Z`

4. Build artifacts:
- `python3 -m pip install build`
- `python3 -m build`

5. Publish artifacts according to your package index policy.
