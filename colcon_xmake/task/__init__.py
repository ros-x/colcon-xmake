from pathlib import Path
import subprocess


def ensure_build_layout(args):
    Path(args.build_base).mkdir(parents=True, exist_ok=True)
    Path(args.install_base).mkdir(parents=True, exist_ok=True)


def run_command(cmd, *, cwd=None, env=None):
    result = subprocess.run(cmd, cwd=cwd, env=env, check=False)
    return result.returncode
