# colcon-xmake

[![CI](https://github.com/ros-x/colcon-xmake/actions/workflows/ci.yml/badge.svg)](https://github.com/ros-x/colcon-xmake/actions/workflows/ci.yml)

A [colcon](https://colcon.readthedocs.io/) plugin that adds [xmake](https://xmake.io/) build and test support for ROS 2 packages.
It provides the `xmake` and `ros.ament_xmake` build types so that ROS 2 workspaces can include packages built with xmake alongside traditional CMake/ament packages.

## Requirements

- Python 3.10+
- colcon-core >= 0.16.0
- xmake

## Installation

Install from PyPI:

```bash
pip install colcon-xmake
```

Or install from source for development:

```bash
git clone https://github.com/ros-x/colcon-xmake.git
cd colcon-xmake
python3 -m pip install -e .
```

## Entry points

- `colcon_core.task.build`
  - `xmake`
  - `ros.ament_xmake`
- `colcon_core.task.test`
  - `xmake`
  - `ros.ament_xmake`
- `colcon_core.package_identification`
  - `xmake` (optional generic identification via `xmake.lua`)

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

## Related projects

See the [ros-x](https://github.com/ros-x) organization for related projects.

## License

Apache License 2.0 -- see [LICENSE](LICENSE) for details.
