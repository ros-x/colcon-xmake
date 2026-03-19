import shutil

from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.shell import get_command_environment
from colcon_core.task import TaskExtensionPoint

from colcon_xmake.task.xmake import XMAKE_EXECUTABLE
from colcon_xmake.task import run_command

logger = colcon_logger.getChild(__name__)


class XmakeTestTask(TaskExtensionPoint):
    """Test packages with xmake."""

    def __init__(self):
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):
        parser.add_argument(
            '--xmake-test-args', nargs='*', metavar='*', type=str.lstrip,
            help='Pass arguments to xmake test step')

    async def test(self):
        args = self.context.args
        logger.info(f"Testing xmake package in '{args.path}'")

        if not shutil.which(XMAKE_EXECUTABLE):
            logger.error("Could not find 'xmake' executable in PATH")
            return 1

        try:
            env = await get_command_environment(
                'test', args.build_base, self.context.dependencies)
        except RuntimeError as e:
            logger.error(str(e))
            return 1

        cmd = [XMAKE_EXECUTABLE, 'test'] + (args.xmake_test_args or [])
        return await run_command(
            self.context, cmd, cwd=str(args.path), env=env)
