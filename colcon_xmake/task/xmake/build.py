import shutil
import re
import xml.etree.ElementTree as ET
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


def _split_cmake_list(raw):
    value = raw.strip()
    if not value:
        return []
    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    if ';' in value:
        return [part for part in value.split(';') if part]
    return [part for part in value.split() if part]


def _resolve_cmake_value(raw_value, set_values):
    value = raw_value.strip()
    if not value:
        return []

    unquoted = value
    if value.startswith('"') and value.endswith('"'):
        unquoted = value[1:-1].strip()

    if unquoted.startswith('${') and unquoted.endswith('}'):
        ref_name = unquoted[2:-1]
        return list(set_values.get(ref_name, []))
    return _split_cmake_list(value)


def _parse_cmake_set_map(path):
    if not path.is_file():
        return {}
    text = path.read_text(encoding='utf-8', errors='ignore')
    set_values = {}
    pattern = re.compile(
        r'set\(\s*([A-Za-z0-9_]+)\s+(.+?)\s*\)',
        re.MULTILINE | re.DOTALL)
    for match in pattern.finditer(text):
        variable = match.group(1).strip()
        raw_value = match.group(2).strip()
        set_values[variable] = _resolve_cmake_value(raw_value, set_values)
    return set_values


def _parse_set_value(path, variable):
    set_values = _parse_cmake_set_map(path)
    if variable not in set_values:
        return []
    return list(set_values[variable])


def _replace_pkg_dir(parts, pkg, cmake_dir):
    marker = '${' + pkg + '_DIR}'
    return [part.replace(marker, str(cmake_dir)) for part in parts]


def _find_library(prefix, name):
    libdir = prefix / 'lib'
    for ext in ('.so', '.dylib', '.a'):
        candidate = libdir / f'lib{name}{ext}'
        if candidate.is_file():
            return str(candidate)
    return None


def _append_unique(dst, values):
    for value in values:
        if value and value not in dst:
            dst.append(value)


def _parse_package_xml_dependencies(path):
    if not path.is_file():
        return []
    try:
        root = ET.fromstring(path.read_text(encoding='utf-8', errors='ignore'))
    except ET.ParseError:
        return []

    deps = []
    dep_tags = (
        'depend',
        'build_depend',
        'build_export_depend',
        'exec_depend',
    )
    for tag in dep_tags:
        for node in root.findall(tag):
            if node.text:
                value = node.text.strip()
                if value and value not in deps:
                    deps.append(value)
    return deps


def _generate_ros_index_file(build_base, ament_prefix_path):
    Path(build_base).mkdir(parents=True, exist_ok=True)
    prefixes = [Path(p) for p in (ament_prefix_path or '').split(':') if p]
    index = {}
    for prefix in prefixes:
        share_dir = prefix / 'share'
        if not share_dir.is_dir():
            continue
        for pkg_dir in share_dir.iterdir():
            if not pkg_dir.is_dir():
                continue
            pkg = pkg_dir.name
            cmake_dir = pkg_dir / 'cmake'
            dep_file = cmake_dir / 'ament_cmake_export_dependencies-extras.cmake'
            inc_file = cmake_dir / 'ament_cmake_export_include_directories-extras.cmake'
            lib_file = cmake_dir / 'ament_cmake_export_libraries-extras.cmake'
            def_file = cmake_dir / 'ament_cmake_export_definitions-extras.cmake'
            pkg_xml = pkg_dir / 'package.xml'
            has_extras = dep_file.is_file() or inc_file.is_file() or lib_file.is_file() or def_file.is_file()
            has_pkg_xml = pkg_xml.is_file()
            if not has_extras and not has_pkg_xml:
                continue

            include_dirs = []
            if inc_file.is_file():
                include_dirs = _replace_pkg_dir(
                    _parse_set_value(inc_file, '_exported_include_dirs'),
                    pkg, cmake_dir)
            compile_definitions = []
            if def_file.is_file():
                compile_definitions = _parse_set_value(def_file, '_exported_definitions')
            dependencies = []
            _append_unique(dependencies, _parse_set_value(dep_file, '_exported_dependencies'))
            _append_unique(dependencies, _parse_package_xml_dependencies(pkg_xml))
            exported_libraries = _parse_set_value(lib_file, '_exported_libraries')
            pkg_include_dir = prefix / 'include' / pkg
            if pkg_include_dir.is_dir():
                _append_unique(include_dirs, [str(pkg_include_dir)])

            link_flags = []
            rpath_dirs = []
            for item in exported_libraries:
                if item.startswith('-'):
                    _append_unique(link_flags, [item])
                    continue
                if Path(item).is_absolute() and Path(item).is_file():
                    _append_unique(link_flags, [item])
                    _append_unique(rpath_dirs, [str(Path(item).parent)])
                    continue
                resolved = _find_library(prefix, item)
                if resolved:
                    _append_unique(link_flags, [resolved])
                    _append_unique(rpath_dirs, [str(Path(resolved).parent)])
                else:
                    _append_unique(link_flags, [f'-L{prefix / "lib"}', f'-l{item}'])
                    _append_unique(rpath_dirs, [str(prefix / 'lib')])

            index[pkg] = {
                'include_dirs': include_dirs,
                'compile_definitions': compile_definitions,
                'link_flags': link_flags,
                'rpath_dirs': rpath_dirs,
                'dependencies': dependencies,
            }

    index_path = Path(build_base) / 'colcon_xmake_ros_index.lua'
    lines = ['_AMENT_XMAKE_ROS_INDEX = {']
    for pkg in sorted(index.keys()):
        meta = index[pkg]
        lines.append(f'  ["{_lua_quote(pkg)}"] = {{')
        for key in ('include_dirs', 'compile_definitions', 'link_flags', 'rpath_dirs', 'dependencies'):
            lines.append(f'    {key} = {{')
            for value in meta[key]:
                lines.append(f'      "{_lua_quote(value)}",')
            lines.append('    },')
        lines.append('  },')
    lines.append('}')
    index_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return str(index_path)


def _write_entry_file(build_base, project_path, rule_file, index_file=None):
    path = Path(build_base) / 'colcon_xmake_entry.lua'
    lines = []
    if index_file:
        lines.append(f'includes("{_lua_quote(index_file)}")')
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
        index_file = _generate_ros_index_file(
            args.build_base, env.get('AMENT_PREFIX_PATH'))
        entry_file = _write_entry_file(
            args.build_base, str(args.path), rule_file, index_file=index_file)

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
