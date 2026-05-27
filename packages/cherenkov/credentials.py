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
        import secrets

        path = cls.get_env_path()
        if not path.exists():
            # Generate a secure random secret on first run
            new_secret = secrets.token_urlsafe(32)
            cls.set_jwt_secret(new_secret)
            cls.set_rotation_flag()
            return new_secret

        content = path.read_text()
        secret = ""  # nosec B105
        for line in content.splitlines():
            if line.strip().startswith("CHERENKOV_JWT_SECRET="):  # nosec B105
                secret = line.split("CHERENKOV_JWT_SECRET=", 1)[-1].strip()  # nosec B105
                break

        if not secret or secret in _BAD_SECRETS:
            # Regenerate if secret is missing or insecure
            new_secret = secrets.token_urlsafe(32)
            cls.set_jwt_secret(new_secret)
            cls.set_rotation_flag()
            return new_secret

        return secret

    @classmethod
    def enforce_credentials_rotation(cls, new_secret: str) -> None:
        """Enforces rotation of first-run credentials and clears the blocker flag."""
        if os.environ.get("CHERENKOV_FORCE_ROTATION") == "true":
            os.environ["CHERENKOV_FORCE_ROTATION"] = "false"
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
            if line.strip().startswith("CHERENKOV_JWT_SECRET="):  # nosec B105
                new_lines.append(f"CHERENKOV_JWT_SECRET={new_secret}\n")  # nosec B105
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"CHERENKOV_JWT_SECRET={new_secret}\n")  # nosec B105
        content = "".join(new_lines)

        # Securely write the file with restricted permissions to avoid CodeQL clear-text storage alert
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        mode = 0o600
        fd = os.open(path, flags, mode)
        with open(fd, "w", encoding="utf-8") as f:
            f.write(content)

        cls.clear_rotation_flag()
