from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import MusubiError, PROFILES, create_project, doctor, load_profile, validate_project


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="musubi", description="Conecta sistemas, APIs e IA sobre Zato 4.1")
    root.add_argument("--version", action="version", version=f"musubi {__version__}")
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="crea un proyecto desde una plantilla")
    init.add_argument("name")
    init.add_argument("--profile", choices=PROFILES, default="dev")
    init.add_argument("--output", type=Path)
    init.add_argument("--domain")
    init.add_argument("--force", action="store_true")

    commands.add_parser("profiles", help="lista los perfiles incluidos")
    for command in ("validate", "doctor"):
        check = commands.add_parser(command, help=f"{command} un proyecto generado")
        check.add_argument("path", type=Path, nargs="?", default=Path.cwd())
        if command == "validate":
            check.add_argument("--strict", action="store_true")
    return root


def print_checks(checks: list[object]) -> int:
    failed = False
    for check in checks:
        marker = "OK" if check.ok else "FAIL"
        print(f"[{marker}] {check.message}")
        failed = failed or not check.ok
    return 1 if failed else 0


def run(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "profiles":
            for name in PROFILES:
                profile = load_profile(name)
                print(f"{name:5} {profile['description']}")
            return 0
        if args.command == "init":
            destination = args.output or Path(args.name)
            files = create_project(destination, args.name, args.profile, args.domain, args.force)
            print(f"Proyecto {args.name} creado en {destination} ({len(files)} archivos, perfil {args.profile})")
            return 0
        if args.command == "validate":
            return print_checks(validate_project(args.path, args.strict))
        if args.command == "doctor":
            return print_checks(doctor(args.path))
    except MusubiError as exc:
        print(f"musubi: {exc}", file=sys.stderr)
        return 2
    return 0


def main() -> None:
    raise SystemExit(run())
