import shutil
from pathlib import Path

from colcon_core.logging import colcon_logger
from colcon_core.plugin_system import satisfies_version
from colcon_core.shell import get_command_environment
from colcon_core.task import TaskExtensionPoint

from colcon_xmake.task import ensure_build_layout
from colcon_xmake.task import normalize_timeout
from colcon_xmake.task import run_command
from colcon_xmake.task.xmake import XMAKE_EXECUTABLE
from colcon_xmake.task.xmake import resolve_ament_xmake_rule_file

logger = colcon_logger.getChild(__name__)


def _lua_quote(text):
    return text.replace('\\', '\\\\').replace('"', '\\"')


def _write_entry_file(build_base, project_path, rule_file):
    path = Path(build_base) / 'colcon_xmake_entry.lua'
    lines = []
    if rule_file:
        lines.append(f'includes("{_lua_quote(rule_file)}")')
    lines.append(f'includes("{_lua_quote(str(Path(project_path) / "xmake.lua"))}")')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return str(path)


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
        parser.add_argument(
            '--xmake-timeout', type=normalize_timeout,
            help='Timeout in seconds for each xmake command')
        parser.add_argument(
            '--xmake-skip-install', action='store_true',
            help='Skip xmake install step')

    async def build(self):
        args = self.context.args
        logger.info(f"Building xmake package in '{args.path}'")

        disallowed = ('--builddir', '-o', '--installdir')
        for value in args.xmake_config_args or []:
            if value.startswith(disallowed):
                logger.error(
                    "Do not pass build/install directory flags via "
                    "--xmake-config-args; they are managed by colcon")
                return 2

        if not shutil.which(XMAKE_EXECUTABLE):
            logger.error("Could not find 'xmake' executable in PATH")
            return 1

        try:
            env = await get_command_environment(
                'build', args.build_base, self.context.dependencies)
        except RuntimeError as e:
            logger.error(str(e))
            return 1
        if getattr(args, 'symlink_install', False):
            env['AMENT_XMAKE_SYMLINK_INSTALL'] = '1'
        env['AMENT_XMAKE_SOURCE_DIR'] = str(args.path)
        rule_file = resolve_ament_xmake_rule_file(env.get('AMENT_PREFIX_PATH'))
        if rule_file:
            env['AMENT_XMAKE_RULE_FILE'] = rule_file
        pkg_type = getattr(self.context.pkg, 'type', None)
        if pkg_type == 'ros.ament_xmake' and not rule_file:
            logger.error(
                "Could not resolve ament_xmake rule file from AMENT_PREFIX_PATH. "
                "Build/install 'ament_xmake' first and source the workspace setup.")
            return 1
        entry_file = _write_entry_file(
            args.build_base, str(args.path), rule_file)

        ensure_build_layout(args)

        config_cmd = [
            XMAKE_EXECUTABLE, 'f',
            '--yes',
            '--builddir=' + args.build_base,
            '--file=' + entry_file,
        ] + (args.xmake_config_args or [])
        rc = await run_command(
            self.context, config_cmd, cwd=str(args.path), env=env,
            timeout=args.xmake_timeout)
        if rc:
            if rc == 124:
                logger.error("xmake configure step timed out")
            return rc

        build_cmd = [
            XMAKE_EXECUTABLE, 'build',
            '--file=' + entry_file,
        ] + (args.xmake_build_args or [])
        rc = await run_command(
            self.context, build_cmd, cwd=str(args.path), env=env,
            timeout=args.xmake_timeout)
        if rc:
            if rc == 124:
                logger.error("xmake build step timed out")
            return rc

        if args.xmake_skip_install:
            return 0

        install_cmd = [
            XMAKE_EXECUTABLE, 'install',
            '--yes',
            '-o', args.install_base,
            '--file=' + entry_file,
        ] + (args.xmake_install_args or [])
        return await run_command(
            self.context, install_cmd, cwd=str(args.path), env=env,
            timeout=args.xmake_timeout)
