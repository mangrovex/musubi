from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from musubi.cli import run


class CliTests(TestCase):
    def test_profiles(self):
        output = StringIO()
        with redirect_stdout(output):
            code = run(["profiles"])
        self.assertEqual(code, 0)
        self.assertIn("prod", output.getvalue())

    def test_init_and_validate(self):
        with TemporaryDirectory() as directory:
            target = Path(directory) / "demo"
            self.assertEqual(run(["init", "demo", "--output", str(target)]), 0)
            self.assertEqual(run(["validate", str(target)]), 0)
