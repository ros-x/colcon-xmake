from pathlib import Path

from colcon_xmake.package_identification.xmake import XmakePackageIdentification


class Metadata:
    def __init__(self, path):
        self.path = Path(path)
        self.type = None
        self.name = None
        self.dependencies = {'build': set(), 'run': set(), 'test': set()}


def test_identify_xmake(tmp_path):
    (tmp_path / 'xmake.lua').write_text('set_project("demo")\n', encoding='utf-8')
    m = Metadata(tmp_path)
    ext = XmakePackageIdentification()

    ext.identify(m)

    assert m.type == 'xmake'
    assert m.name == tmp_path.name


def test_skip_non_xmake(tmp_path):
    m = Metadata(tmp_path)
    ext = XmakePackageIdentification()

    ext.identify(m)

    assert m.type is None
    assert m.name is None
