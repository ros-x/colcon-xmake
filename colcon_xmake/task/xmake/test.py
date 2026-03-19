import shutil
import time

from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.shell import get_command_environment
from colcon_core.task import TaskExtensionPoint

from colcon_xmake.task import normalize_timeout
from colcon_xmake.task.xmake import XMAKE_EXECUTABLE
from colcon_xmake.task import run_command
from colcon_xmake.task.test_result import write_junit_result

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
        parser.add_argument(
            '--xmake-timeout', type=normalize_timeout,
            help='Timeout in seconds for each xmake command')

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
        start = time.time()
        rc = await run_command(
            self.context, cmd, cwd=str(args.path), env=env,
            timeout=args.xmake_timeout)
        duration = time.time() - start

        if rc == 124:
            logger.error("xmake test step timed out")

        if args.test_result_base:
            write_junit_result(
                args.test_result_base, self.context.pkg.name, rc, duration)

        return rc
