from pathlib import Path

from colcon_xmake.task.xmake import resolve_ament_xmake_rule_file


def test_resolve_ament_xmake_rule_file(tmp_path):
    prefix1 = tmp_path / 'prefix1'
    prefix2 = tmp_path / 'prefix2'
    rule = prefix2 / 'share' / 'ament_xmake' / 'xmake' / 'rules' / 'ament_xmake' / 'package.lua'
    rule.parent.mkdir(parents=True)
    rule.write_text('-- rule', encoding='utf-8')

    path = f"{prefix1}:{prefix2}"
    resolved = resolve_ament_xmake_rule_file(path)
    assert resolved == str(rule)


def test_resolve_ament_xmake_rule_file_none(tmp_path):
    resolved = resolve_ament_xmake_rule_file(str(tmp_path))
    assert resolved is None
