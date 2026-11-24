from __future__ import annotations

import re
import shutil
import tomllib
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path


TOKEN = re.compile(r"{{\s*([a-zA-Z0-9_]+)\s*}}")
PROFILES = ("dev", "stage", "prod")
SPECIAL_TEMPLATE_NAMES = {
    "dot-env.example.tmpl": ".env.example",
    "dot-gitignore.tmpl": ".gitignore",
}


class MusubiError(RuntimeError):
    pass


def profile_path(name: str) -> Path:
    if name not in PROFILES:
        raise MusubiError(f"Perfil desconocido: {name}")
    return Path(str(files("musubi").joinpath("profiles", f"{name}.toml")))


def load_profile(name: str) -> dict[str, object]:
    with profile_path(name).open("rb") as stream:
        return tomllib.load(stream)


def render_text(source: str, context: dict[str, object]) -> str:
    missing: set[str] = set()

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in context:
            missing.add(key)
            return match.group(0)
        value = context[key]
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    rendered = TOKEN.sub(replace, source)
    if missing:
        raise MusubiError(f"Variables sin resolver: {', '.join(sorted(missing))}")
    return rendered


def create_project(
    destination: Path,
    name: str,
    profile_name: str,
    domain: str | None = None,
    force: bool = False,
) -> list[Path]:
    if destination.exists() and any(destination.iterdir()) and not force:
        raise MusubiError(f"El destino no está vacío: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    profile = load_profile(profile_name)
    context = {
        **profile,
        "project_name": name,
        "profile": profile_name,
        "domain": domain or str(profile["default_domain"]),
    }
    template_root = Path(str(files("musubi").joinpath("templates", "project")))
    created: list[Path] = []
    for source in sorted(template_root.rglob("*")):
        if not source.is_file():
            continue
        relative = source.relative_to(template_root)
        target_name = SPECIAL_TEMPLATE_NAMES.get(
            relative.name, relative.name.removesuffix(".tmpl")
        )
        target = destination / relative.with_name(target_name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render_text(source.read_text(), context))
        if target.suffix == ".sh":
            target.chmod(0o755)
        created.append(target)
    return created


@dataclass(frozen=True)
class Check:
    ok: bool
    message: str


def validate_project(root: Path, strict: bool = False) -> list[Check]:
    required = (
        "compose.yaml",
        ".env.example",
        "caddy/Caddyfile",
        "zato/enmasse/enmasse.yaml",
        "zato/services/health.py",
    )
    checks = [Check((root / item).is_file(), f"archivo {item}") for item in required]
    compose = (root / "compose.yaml")
    if compose.is_file():
        text = compose.read_text()
        checks.append(Check("zatosource/zato-4.1" in text, "imagen base Zato 4.1"))
        checks.append(Check("{{" not in text, "sin variables de plantilla pendientes"))
    env_file = root / ".env.example"
    if env_file.is_file():
        env_text = env_file.read_text()
        checks.append(Check("CHANGE_ME" in env_text, "secretos marcados para reemplazo"))
        if strict:
            image_line = next((line for line in env_text.splitlines() if line.startswith("ZATO_IMAGE=")), "")
            checks.append(Check("@sha256:" in image_line, "imagen fijada por digest"))
    return checks


def doctor(root: Path) -> list[Check]:
    return [
        Check(shutil.which("docker") is not None, "Docker disponible"),
        Check(shutil.which("git") is not None, "Git disponible"),
        *validate_project(root),
    ]
