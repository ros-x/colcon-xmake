from colcon_core.package_identification import PackageIdentificationExtensionPoint
from colcon_core.plugin_system import satisfies_version


class XmakePackageIdentification(PackageIdentificationExtensionPoint):
    """Identify xmake projects by xmake.lua."""

    def __init__(self):
        super().__init__()
        satisfies_version(
            PackageIdentificationExtensionPoint.EXTENSION_POINT_VERSION,
            '^1.0')

    def identify(self, metadata):
        if metadata.type is not None and metadata.type != 'xmake':
            return
        if not (metadata.path / 'xmake.lua').is_file():
            return

        metadata.type = 'xmake'
        if metadata.name is None:
            metadata.name = metadata.path.name
