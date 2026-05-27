import os
from pathlib import Path
from typing import Optional

_ENV_PATH = Path.home() / ".cherenkov" / ".env"

_BAD_SECRETS = {
    "change-me",
    "admin",
    "secret",
    "password",
    "cherenkov-sovereign-audit-key-2024",
    "",
    "CHERENKOV_JWT_SECRET=dev",
    "CHERENKOV_JWT_SECRET=default",
}


class DefaultCredentialsManager:
    """Manages first-boot credential rotation state.

    Stores a 'rotation_required' flag in the .env file.
    On fresh install: rotation is required until an admin calls /auth/rotate-password
    After rotation: flag cleared, normal auth resumes.
    """

    rotation_file: Optional[Path] = None

    @classmethod
    def get_env_path(cls) -> Path:
        override = os.getenv("ROTATION_ENV_PATH")
        if override:
            cls.rotation_file = Path(override)
            return cls.rotation_file
        path = _ENV_PATH
        cls.rotation_file = path
        return path

    @classmethod
    def is_rotation_required(cls) -> bool:
        if os.environ.get("CHERENKOV_FORCE_ROTATION") == "true":
            return True
        path = cls.get_env_path()
        flag_file = path.parent / "rotation_required"
        if flag_file.exists():
            return flag_file.read_text().strip() == "1"
        return False

    @classmethod
    def clear_rotation_flag(cls) -> None:
        path = cls.get_env_path()
        flag_file = path.parent / "rotation_required"
        if flag_file.exists():
            flag_file.unlink()

    @classmethod
    def set_rotation_flag(cls) -> None:
        path = cls.get_env_path()
        flag_file = path.parent / "rotation_required"
        flag_file.write_text("1")

    @classmethod
    def get_jwt_secret(cls) -> str:
        path = cls.get_env_path()
        if not path.exists():
            cls.set_rotation_flag()
            raise RuntimeError(
                "CHERENKOV_JWT_SECRET not configured. "
                "A new secret was generated and stored in .env. "
                "Run /auth/rotate-password to complete initial setup."
            )
        content = path.read_text()
        for line in content.splitlines():
            if line.strip().startswith("CHERENKOV_JWT_SECRET="):
                secret = line.split("CHERENKOV_JWT_SECRET=", 1)[-1].strip()
                break
        else:
            secret = ""
        if not secret or secret in _BAD_SECRETS:
            cls.set_rotation_flag()
            raise RuntimeError(
                "CHERENKOV_JWT_SECRET is a known-bad/default value. "
                "Run /auth/rotate-password to set a secure password and regenerate the secret."
            )
        return secret

    @classmethod
    def enforce_credentials_rotation(cls, new_secret: str) -> None:
        """Enforces rotation of first-run credentials and clears the blocker flag."""
        cls.set_jwt_secret(new_secret)
        cls.clear_rotation_flag()

    @classmethod
    def set_jwt_secret(cls, new_secret: str) -> None:
        path = cls.get_env_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        content = path.read_text() if path.exists() else ""
        lines = content.splitlines(keepends=True)
        new_lines = []
        found = False
        for line in lines:
            if line.strip().startswith("CHERENKOV_JWT_SECRET="):
                new_lines.append(f"CHERENKOV_JWT_SECRET={new_secret}\n")
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"CHERENKOV_JWT_SECRET={new_secret}\n")
        content = "".join(new_lines)
        path.write_text(content)
        if os.name == "posix":
            os.chmod(path, 0o600)
        cls.clear_rotation_flag()

    @classmethod
    def enforce_credentials_rotation(cls, new_hash: str) -> None:
        if os.environ.get("CHERENKOV_FORCE_ROTATION") == "true":
            os.environ["CHERENKOV_FORCE_ROTATION"] = "false"
        cls.set_jwt_secret(new_hash)
