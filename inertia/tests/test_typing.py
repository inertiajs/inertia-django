from pathlib import Path
from unittest import TestCase


class PyTypedTestCase(TestCase):
    def test_py_typed_marker_exists(self):
        """Verify the py.typed marker exists for PEP 561 compliance."""
        package_dir = Path(__file__).resolve().parent.parent
        self.assertTrue((package_dir / "py.typed").exists())
