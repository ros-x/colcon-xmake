import argparse

from colcon_xmake.task.ament_xmake.build import AmentXmakeBuildTask
from colcon_xmake.task.ament_xmake.test import AmentXmakeTestTask
from colcon_xmake.task.xmake.build import XmakeBuildTask
from colcon_xmake.task.xmake.test import XmakeTestTask


def test_xmake_build_arguments_registration():
    parser = argparse.ArgumentParser()
    ext = XmakeBuildTask()
    ext.add_arguments(parser=parser)
    args = parser.parse_args([])
    assert hasattr(args, 'xmake_config_args')
    assert hasattr(args, 'xmake_build_args')
    assert hasattr(args, 'xmake_install_args')
    assert hasattr(args, 'xmake_timeout')
    assert hasattr(args, 'xmake_skip_install')


def test_xmake_test_arguments_registration():
    parser = argparse.ArgumentParser()
    ext = XmakeTestTask()
    ext.add_arguments(parser=parser)
    args = parser.parse_args([])
    assert hasattr(args, 'xmake_test_args')
    assert hasattr(args, 'xmake_timeout')


def test_ament_xmake_build_arguments_registration():
    parser = argparse.ArgumentParser()
    ext = AmentXmakeBuildTask()
    ext.add_arguments(parser=parser)
    args = parser.parse_args([])
    assert hasattr(args, 'ament_xmake_args')


def test_ament_xmake_test_arguments_registration():
    parser = argparse.ArgumentParser()
    ext = AmentXmakeTestTask()
    ext.add_arguments(parser=parser)
    args = parser.parse_args([])
    assert hasattr(args, 'ament_xmake_test_args')
