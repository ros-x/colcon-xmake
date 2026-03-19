from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.task import TaskExtensionPoint

from colcon_xmake.task import ensure_build_layout
from colcon_xmake.task import run_command
from colcon_xmake.task.xmake import XMAKE_EXECUTABLE

logger = colcon_logger.getChild(__name__)


class XmakeBuildTask(TaskExtensionPoint):
    """Build packages with xmake."""

    def __init__(self):
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):
        parser.add_argument(
            '--xmake-config-args', nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to xmake configure step')
        parser.add_argument(
            '--xmake-build-args', nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to xmake build step')
        parser.add_argument(
            '--xmake-install-args', nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to xmake install step')

    async def build(self):
        args = self.context.args
        logger.info(f"Building xmake package in '{args.path}'")

        ensure_build_layout(args)

        config_cmd = [
            XMAKE_EXECUTABLE, 'f',
            '--buildir=' + args.build_base,
            '--installdir=' + args.install_base,
        ] + (args.xmake_config_args or [])
        rc = run_command(config_cmd, cwd=args.path)
        if rc:
            return rc

        build_cmd = [XMAKE_EXECUTABLE] + (args.xmake_build_args or [])
        rc = run_command(build_cmd, cwd=args.path)
        if rc:
            return rc

        install_cmd = [XMAKE_EXECUTABLE, 'install'] + (args.xmake_install_args or [])
        return run_command(install_cmd, cwd=args.path)
