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
