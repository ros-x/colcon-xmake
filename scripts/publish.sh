#!/bin/bash
# Build and publish colcon-xmake to PyPI
#
# Dependency: pip install build twine
#
# Usage:
#   ./scripts/publish.sh build      # build only
#   ./scripts/publish.sh upload      # upload dist/ to PyPI (no rebuild)
#   ./scripts/publish.sh upload test # upload dist/ to TestPyPI
#   ./scripts/publish.sh            # build + upload to PyPI
#   ./scripts/publish.sh test       # build + upload to TestPyPI

set -e

cd "$(dirname "$0")/.."

do_build() {
    rm -rf dist build *.egg-info
    echo "Building..."
    python3 -m build
    echo "Built: $(ls dist/)"
}

do_upload() {
    if [ ! -d dist ] || [ -z "$(ls dist/ 2>/dev/null)" ]; then
        echo "Error: dist/ is empty. Run './scripts/publish.sh build' first."
        exit 1
    fi
    if [ "$1" = "test" ]; then
        echo "Uploading to TestPyPI..."
        python3 -m twine upload --repository testpypi dist/* --verbose
        echo "Install with: pip install --index-url https://test.pypi.org/simple/ colcon-xmake"
    else
        echo "Uploading to PyPI..."
        python3 -m twine upload dist/* --verbose
        echo "Install with: pip install colcon-xmake"
    fi
}

case "$1" in
    build)
        do_build
        ;;
    upload)
        do_upload "$2"
        ;;
    test)
        do_build
        do_upload test
        ;;
    "")
        do_build
        do_upload
        ;;
    *)
        echo "Usage: $0 {build|upload [test]|test|}"
        exit 1
        ;;
esac
