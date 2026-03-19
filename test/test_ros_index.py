from pathlib import Path

from colcon_xmake.task.xmake.build import _generate_ros_index_file
from colcon_xmake.task.xmake.build import _parse_package_xml_dependencies
from colcon_xmake.task.xmake.build import _parse_set_value


def test_parse_set_value_variable_reference(tmp_path):
    cmake_file = tmp_path / 'deps.cmake'
    cmake_file.write_text(
        '\n'.join([
            'set(_exported_dependencies "a;b;c")',
            'set(example_DEPENDENCIES ${_exported_dependencies})',
        ]) + '\n',
        encoding='utf-8')

    assert _parse_set_value(cmake_file, '_exported_dependencies') == ['a', 'b', 'c']
    assert _parse_set_value(cmake_file, 'example_DEPENDENCIES') == ['a', 'b', 'c']


def test_parse_set_value_multiline(tmp_path):
    cmake_file = tmp_path / 'deps_multiline.cmake'
    cmake_file.write_text(
        '\n'.join([
            'set(_exported_dependencies',
            '  "foo;bar;baz"',
            ')',
        ]) + '\n',
        encoding='utf-8')

    assert _parse_set_value(cmake_file, '_exported_dependencies') == ['foo', 'bar', 'baz']


def test_parse_package_xml_dependencies(tmp_path):
    package_xml = tmp_path / 'package.xml'
    package_xml.write_text(
        '\n'.join([
            '<package format="3">',
            '  <name>demo_pkg</name>',
            '  <version>0.0.1</version>',
            '  <description>demo</description>',
            '  <maintainer email="demo@example.com">demo</maintainer>',
            '  <license>Apache-2.0</license>',
            '  <depend>rclcpp</depend>',
            '  <build_export_depend>geometry_msgs</build_export_depend>',
            '  <exec_depend>std_msgs</exec_depend>',
            '</package>',
        ]) + '\n',
        encoding='utf-8')

    deps = _parse_package_xml_dependencies(package_xml)
    assert deps == ['rclcpp', 'geometry_msgs', 'std_msgs']


def test_generate_ros_index_with_package_xml_fallback(tmp_path):
    prefix = tmp_path / 'prefix'
    share = prefix / 'share'
    include = prefix / 'include'

    demo_share = share / 'demo_pkg'
    demo_share.mkdir(parents=True)
    (demo_share / 'package.xml').write_text(
        '\n'.join([
            '<package format="3">',
            '  <name>demo_pkg</name>',
            '  <version>0.0.1</version>',
            '  <description>demo</description>',
            '  <maintainer email="demo@example.com">demo</maintainer>',
            '  <license>Apache-2.0</license>',
            '  <depend>rosidl_default_runtime</depend>',
            '</package>',
        ]) + '\n',
        encoding='utf-8')

    runtime_share = share / 'rosidl_default_runtime'
    runtime_share.mkdir(parents=True)
    (runtime_share / 'package.xml').write_text(
        '\n'.join([
            '<package format="3">',
            '  <name>rosidl_default_runtime</name>',
            '  <version>0.0.1</version>',
            '  <description>runtime</description>',
            '  <maintainer email="demo@example.com">demo</maintainer>',
            '  <license>Apache-2.0</license>',
            '  <depend>rosidl_typesupport_introspection_cpp</depend>',
            '</package>',
        ]) + '\n',
        encoding='utf-8')

    introspection_share = share / 'rosidl_typesupport_introspection_cpp'
    introspection_share.mkdir(parents=True)
    (introspection_share / 'package.xml').write_text(
        '\n'.join([
            '<package format="3">',
            '  <name>rosidl_typesupport_introspection_cpp</name>',
            '  <version>0.0.1</version>',
            '  <description>introspection</description>',
            '  <maintainer email="demo@example.com">demo</maintainer>',
            '  <license>Apache-2.0</license>',
            '</package>',
        ]) + '\n',
        encoding='utf-8')

    (include / 'rosidl_typesupport_introspection_cpp').mkdir(parents=True)
    (include / 'rosidl_typesupport_introspection_cpp' / 'marker.hpp').write_text(
        '// marker\n', encoding='utf-8')

    index_file = _generate_ros_index_file(tmp_path / 'build', str(prefix))
    text = Path(index_file).read_text(encoding='utf-8')

    assert '["demo_pkg"]' in text
    assert '["rosidl_default_runtime"]' in text
    assert '["rosidl_typesupport_introspection_cpp"]' in text
    assert '"rosidl_typesupport_introspection_cpp"' in text
    assert str(include / 'rosidl_typesupport_introspection_cpp') in text
