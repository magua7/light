import os
from pathlib import Path


def read_bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    def __init__(self):
        self.app_name: str = "净光物联城市光污染多模态感知监测与智能评级系统"
        self.api_prefix: str = "/api"
        self.project_dir: Path = Path(__file__).resolve().parents[2]
        self.upload_dir: Path = self.project_dir / "uploads"
        self.database_path: Path = self.project_dir / "light_inspector.db"
        self.cors_origins: list[str] = ["*"]
        self.jwt_secret_key: str = os.getenv(
            "JWT_SECRET_KEY",
            "light-inspector-production-secret-change-me",
        )
        self.jwt_algorithm: str = "HS256"
        self.jwt_expire_minutes: int = 60 * 24 * 7

        self.light_inspector_enabled: bool = read_bool_env("LIGHT_INSPECTOR_ENABLED", True)
        self.light_inspector_assets_dir: Path = Path(
            os.getenv(
                "LIGHT_INSPECTOR_ASSETS_DIR",
                str(self.project_dir / "model_assets" / "light_inspector"),
            )
        )
        self.light_inspector_model_path: Path = Path(
            os.getenv(
                "LIGHT_INSPECTOR_MODEL_PATH",
                str(self.light_inspector_assets_dir / "best2.pt"),
            )
        )
        self.light_inspector_score_tif: Path = Path(
            os.getenv(
                "LIGHT_INSPECTOR_SCORE_TIF",
                str(self.light_inspector_assets_dir / "score_total.tif"),
            )
        )

        cover_override = os.getenv("LIGHT_INSPECTOR_COVER_TIF")
        self.light_inspector_cover_tif: Path = (
            Path(cover_override)
            if cover_override
            else self.resolve_default_cover_path(self.light_inspector_assets_dir)
        )
        self.light_inspector_tips_dir: Path = Path(
            os.getenv(
                "LIGHT_INSPECTOR_TIPS_DIR",
                str(self.light_inspector_assets_dir),
            )
        )

    def resolve_default_cover_path(self, assets_dir: Path) -> Path:
        preferred_paths = [
            assets_dir / "cover_huan1.tif",
            assets_dir / "cover_hunan1.tif",
        ]
        for candidate in preferred_paths:
            if candidate.exists():
                return candidate
        return preferred_paths[0]


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.database_path.parent.mkdir(parents=True, exist_ok=True)
settings.light_inspector_assets_dir.mkdir(parents=True, exist_ok=True)
