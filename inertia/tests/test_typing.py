from pathlib import Path
from unittest import TestCase


class PyTypedTestCase(TestCase):
    def test_py_typed_marker_exists(self):
        """Verify that the py.typed marker file exists for PEP 561 compliance."""
        package_dir = Path(__file__).resolve().parent.parent
        py_typed = package_dir / "py.typed"
        self.assertTrue(
            py_typed.exists(),
            f"py.typed marker file is missing from {package_dir}",
        )
