# colcon-xmake

`colcon` extension package that adds xmake build/test support, including ROS package type `ros.ament_xmake`.

## Entry points

- `colcon_core.task.build`
  - `xmake`
  - `ros.ament_xmake`
- `colcon_core.task.test`
  - `xmake`
  - `ros.ament_xmake`
- `colcon_core.package_identification`
  - `xmake` (optional generic identification via `xmake.lua`)

## Install

```bash
python3 -m pip install --break-system-packages -e .
```

## Common usage

```bash
colcon build --packages-up-to demo_xmake_cpp
colcon test --packages-select demo_xmake_cpp
```

## xmake-specific arguments

- `--xmake-config-args`
- `--xmake-build-args`
- `--xmake-install-args`
- `--xmake-test-args`
- `--xmake-timeout <seconds>`
- `--xmake-skip-install` (not valid for `ros.ament_xmake`)

## Notes

- `--builddir` / install layout are managed by the plugin; do not pass these via `--xmake-config-args`.
- `xmake` test results are exported to JUnit XML under `--test-result-base` when available.

## Docs

- `docs/USAGE.md`
- `docs/TESTING.md`
- `docs/RELEASE.md`
- `CHANGELOG.md`
