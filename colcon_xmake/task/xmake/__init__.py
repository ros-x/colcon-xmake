XMAKE_EXECUTABLE = 'xmake'


def resolve_ament_xmake_rule_file(ament_prefix_path):
    if not ament_prefix_path:
        return None
    for prefix in ament_prefix_path.split(':'):
        if not prefix:
            continue
        rulefile = (
            f'{prefix}/share/ament_xmake/xmake/rules/'
            'ament_xmake/package.lua'
        )
        try:
            with open(rulefile, 'r', encoding='utf-8'):
                return rulefile
        except OSError:
            continue
    return None
