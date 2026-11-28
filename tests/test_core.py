from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

from musubi.core import PROFILES, create_project, load_profile, validate_project


class ProfileTests(TestCase):
    def test_all_profiles_target_zato_41(self):
        for name in PROFILES:
            profile = load_profile(name)
            self.assertIn("zatosource/zato-4.1", profile["zato_image"])


class ProjectTests(TestCase):
    def test_renders_each_profile(self):
        for profile in PROFILES:
            with self.subTest(profile=profile), TemporaryDirectory() as directory:
                root = Path(directory)
                created = create_project(root, "demo", profile)
                self.assertGreaterEqual(len(created), 7)
                self.assertTrue((root / ".env.example").is_file())
                self.assertTrue((root / ".gitignore").is_file())
                checks = validate_project(root)
                self.assertTrue(all(check.ok for check in checks), checks)

    def test_refuses_non_empty_directory(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "keep.txt").write_text("keep")
            with self.assertRaisesRegex(RuntimeError, "no está vacío"):
                create_project(root, "demo", "dev")

    def test_rabbitmq_is_opt_in(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            create_project(root / 'default', 'demo', 'dev')
            create_project(root / 'rabbit', 'demo', 'prod', rabbitmq=True)
            self.assertFalse((root / 'default' / 'rabbitmq').exists())
            rabbit = root / 'rabbit' / 'rabbitmq'
            for name in ('Dockerfile', 'harden-amqp.py', 'compose.yaml', 'amqp-enmasse.yaml', 'rabbit_services.py', 'README.md'):
                self.assertTrue((rabbit / name).is_file(), name)
            self.assertIn('amqps://', (rabbit / 'amqp-enmasse.yaml').read_text())
            self.assertNotIn('musubitestonly', (rabbit / 'amqp-enmasse.yaml').read_text())
