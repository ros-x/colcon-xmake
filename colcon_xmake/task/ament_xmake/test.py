from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.task import TaskExtensionPoint

from colcon_xmake.task.xmake.test import XmakeTestTask

logger = colcon_logger.getChild(__name__)


class AmentXmakeTestTask(TaskExtensionPoint):
    """Test ROS packages with build type 'ament_xmake'."""

    def __init__(self):
        super().__init__()
        satisfies_version(TaskExtensionPoint.EXTENSION_POINT_VERSION, '^1.0')

    def add_arguments(self, *, parser):
        parser.add_argument(
            '--ament-xmake-test-args', nargs='*', metavar='*', type=str.lstrip,
            help="Pass test arguments to build type 'ament_xmake' packages")

    async def test(self):
        args = self.context.args
        logger.info(
            f"Testing ROS package in '{args.path}' with build type 'ament_xmake'")

        if args.ament_xmake_test_args:
            if args.xmake_test_args is None:
                args.xmake_test_args = []
            args.xmake_test_args += args.ament_xmake_test_args

        extension = XmakeTestTask()
        extension.set_context(context=self.context)
        return await extension.test()
