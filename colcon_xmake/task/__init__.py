from pathlib import Path

from colcon_core.task import run


def ensure_build_layout(args):
    Path(args.build_base).mkdir(parents=True, exist_ok=True)
    Path(args.install_base).mkdir(parents=True, exist_ok=True)


async def run_command(context, cmd, *, cwd=None, env=None):
    completed = await run(context, cmd, cwd=cwd, env=env)
    return completed.returncode
