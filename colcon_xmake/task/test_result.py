from datetime import datetime
from datetime import timezone
from pathlib import Path


def write_junit_result(base_dir, package_name, return_code, duration_sec):
    base = Path(base_dir)
    pkg_dir = base if base.name == package_name else base / package_name
    pkg_dir.mkdir(parents=True, exist_ok=True)
    report = pkg_dir / 'xmake_test.junit.xml'

    escaped_pkg = package_name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    failures = 1 if return_code else 0
    failure_tag = ''
    if return_code:
        failure_tag = (
            f'<failure message="xmake test exited with code {return_code}">'
            f'xmake test failed with exit code {return_code}'
            '</failure>'
        )

    content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<testsuite name="{escaped_pkg}.xmake" tests="1" failures="{failures}" '
        f'errors="0" skipped="0" time="{duration_sec:.3f}" timestamp="{timestamp}">\n'
        f'  <testcase classname="{escaped_pkg}" name="xmake_test" '
        f'time="{duration_sec:.3f}">{failure_tag}</testcase>\n'
        '</testsuite>\n'
    )
    report.write_text(content, encoding='utf-8')
    return report
