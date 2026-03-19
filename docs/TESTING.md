# colcon-xmake Testing

## Unit tests

```bash
python3 -m pytest -q
```

## Plugin behavior tests covered

- argument registration and validation
- timeout normalization
- xmake package identification
- JUnit result writing

## Integration

Use root repo scripts:
- `scripts/e2e_clean_build.sh`
- `scripts/e2e_negative_checks.sh`
