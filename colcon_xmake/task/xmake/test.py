from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
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
        cmd = [XMAKE_EXECUTABLE, 'test'] + (args.xmake_test_args or [])
        return run_command(cmd, cwd=args.path)
