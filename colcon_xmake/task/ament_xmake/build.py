from pathlib import Path

from colcon_core.environment import create_environment_scripts
from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.task import create_file
from colcon_core.task import install
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

        if getattr(args, 'xmake_skip_install', False):
            logger.error(
                '--xmake-skip-install is not supported for ros.ament_xmake '
                'packages because install artifacts are required for ROS env '
                'setup and package discovery')
            return 2

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
        marker = (
            install_base / 'share' / 'ament_index' / 'resource_index' /
            'packages' / self.context.pkg.name
        )
        manifest = install_base / 'share' / self.context.pkg.name / 'package.xml'
        if not marker.exists():
            logger.warning(
                f"Package '{self.context.pkg.name}' doesn't install an ament "
                'resource index marker explicitly; creating fallback marker')
            create_file(
                args,
                'share/ament_index/resource_index/packages/'
                f'{self.context.pkg.name}'
            )
        if not manifest.exists():
            logger.warning(
                f"Package '{self.context.pkg.name}' doesn't install "
                "'package.xml' explicitly; installing fallback copy")
            install(
                args, 'package.xml',
                f'share/{self.context.pkg.name}/package.xml')

        create_environment_scripts(self.context.pkg, args)
        return 0
