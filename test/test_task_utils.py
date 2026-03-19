import pytest
import argparse

from colcon_xmake.task import normalize_timeout


def test_normalize_timeout_none():
    assert normalize_timeout(None) is None


def test_normalize_timeout_valid():
    assert normalize_timeout('12') == 12.0


def test_normalize_timeout_invalid_value():
    with pytest.raises(argparse.ArgumentTypeError):
        normalize_timeout('abc')


def test_normalize_timeout_non_positive():
    with pytest.raises(argparse.ArgumentTypeError):
        normalize_timeout('0')
