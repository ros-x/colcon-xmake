from pathlib import Path
import asyncio
import argparse

from colcon_core.task import run


def ensure_build_layout(args):
    Path(args.build_base).mkdir(parents=True, exist_ok=True)
    Path(args.install_base).mkdir(parents=True, exist_ok=True)


def normalize_timeout(value):
    if value is None:
        return None
    try:
        timeout = float(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(
            f"Invalid timeout value: {value}") from e
    if timeout <= 0:
        raise argparse.ArgumentTypeError(
            f"Timeout must be > 0, got: {timeout}")
    return timeout


async def run_command(context, cmd, *, cwd=None, env=None, timeout=None):
    try:
        completed = await asyncio.wait_for(
            run(context, cmd, cwd=cwd, env=env), timeout=timeout)
    except asyncio.TimeoutError:
        return 124
    return completed.returncode
