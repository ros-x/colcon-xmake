# colcon-xmake Usage

## Install

```bash
python3 -m pip install --break-system-packages -e .
```

## Build with xmake backend

```bash
colcon build --packages-up-to <pkg>
```

Optional xmake flags:
- `--xmake-config-args`
- `--xmake-build-args`
- `--xmake-install-args`
- `--xmake-timeout <seconds>`
- `--xmake-skip-install` (not supported for `ros.ament_xmake`)

## Test

```bash
colcon test --packages-select <pkg>
colcon test-result --verbose
```

If `--test-result-base` is set, plugin writes `xmake_test.junit.xml`.
