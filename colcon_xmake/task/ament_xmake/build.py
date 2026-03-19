from pathlib import Path

from colcon_core.environment import create_environment_scripts
from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.task import TaskExtensionPoint

from colcon_xmake.task.xmake.build import XmakeBuildTask

logger = colcon_logger.getChild(__name__)


class AmentXmakeBuildTask(TaskExtensionPoint):
    """Build ROS packages with build type 'ament_xmake'."""

    def __init__(self):
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):
        parser.add_argument(
            '--ament-xmake-args', nargs='*', metavar='*', type=str.lstrip,
            help="Pass arguments to ROS packages with build type 'ament_xmake'")

    async def build(self):
        args = self.context.args
        logger.info(
            f"Building ROS package in '{args.path}' with build type 'ament_xmake'")

        if args.ament_xmake_args:
            if args.xmake_config_args is None:
                args.xmake_config_args = []
            args.xmake_config_args += args.ament_xmake_args

        extension = XmakeBuildTask()
        extension.set_context(context=self.context)
        rc = await extension.build()

        if rc:
            return rc

        install_base = Path(args.install_base)
        marker = install_base / 'share' / 'ament_index' / 'resource_index' / 'packages' / self.context.pkg.name
        manifest = install_base / 'share' / self.context.pkg.name / 'package.xml'
        if not marker.exists():
            logger.error(f"Missing ament index marker after build: {marker}")
            return 1
        if not manifest.exists():
            logger.error(f"Missing installed package manifest after build: {manifest}")
            return 1

        create_environment_scripts(self.context.pkg, args)
        return 0
