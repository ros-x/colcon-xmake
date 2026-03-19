from colcon_xmake.task.test_result import write_junit_result


def test_write_junit_result_success(tmp_path):
    report = write_junit_result(tmp_path, 'demo_pkg', 0, 0.42)
    content = report.read_text(encoding='utf-8')
    assert report.exists()
    assert 'failures="0"' in content
    assert 'demo_pkg.xmake' in content


def test_write_junit_result_failure(tmp_path):
    report = write_junit_result(tmp_path, 'demo_pkg', 3, 0.99)
    content = report.read_text(encoding='utf-8')
    assert 'failures="1"' in content
    assert 'exit code 3' in content
