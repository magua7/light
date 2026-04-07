from pathlib import Path


class Settings:
    app_name: str = "城市光污染监测与智能评级系统"
    api_prefix: str = "/api"
    project_dir: Path = Path(__file__).resolve().parents[2]
    upload_dir: Path = project_dir / "uploads"
    database_path: Path = project_dir / "light_inspector.db"
    cors_origins: list[str] = ["*"]
    jwt_secret_key: str = "light-inspector-demo-secret-2026"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.database_path.parent.mkdir(parents=True, exist_ok=True)
