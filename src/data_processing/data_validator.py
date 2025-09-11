"""
Data Validator för IGDB Data
Validerar data quality och consistency
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IGDBDataValidator:
    """Validerar IGDB data quality och consistency"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.processed_dir = self.data_dir / "processed"

    def validate_games_data(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Validerar speldata quality

        Args:
            df: DataFrame med speldata

        Returns:
            Dictionary med validation results
        """
        logger.info(f"Validerar {len(df)} spel")

        validation_results = {
            "total_games": len(df),
            "validation_passed": True,
            "issues": [],
            "statistics": {},
        }

        # Kontrollera obligatoriska kolumner
        required_columns = ["id", "name", "genres", "themes", "platforms"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation_results["issues"].append(
                f"Saknade obligatoriska kolumner: {missing_columns}"
            )
            validation_results["validation_passed"] = False

        # Kontrollera ID uniqueness
        if "id" in df.columns:
            duplicate_ids = df["id"].duplicated().sum()
            if duplicate_ids > 0:
                validation_results["issues"].append(
                    f"Duplicerade ID:n: {duplicate_ids}"
                )
                validation_results["validation_passed"] = False

        # Kontrollera missing values
        missing_data = df.isnull().sum()
        high_missing = missing_data[missing_data > len(df) * 0.5]
        if len(high_missing) > 0:
            validation_results["issues"].append(
                f"Kolumner med >50% missing data: {high_missing.to_dict()}"
            )

        # Kontrollera rating range
        if "rating" in df.columns:
            rating_stats = df["rating"].describe()
            validation_results["statistics"]["rating"] = {
                "min": (
                    float(rating_stats["min"])
                    if pd.notna(rating_stats["min"])
                    else None
                ),
                "max": (
                    float(rating_stats["max"])
                    if pd.notna(rating_stats["max"])
                    else None
                ),
                "mean": (
                    float(rating_stats["mean"])
                    if pd.notna(rating_stats["mean"])
                    else None
                ),
                "std": (
                    float(rating_stats["std"])
                    if pd.notna(rating_stats["std"])
                    else None
                ),
            }

            # IGDB ratings är vanligtvis 0-100
            invalid_ratings = df[(df["rating"] < 0) | (df["rating"] > 100)].shape[0]
            if invalid_ratings > 0:
                validation_results["issues"].append(
                    f"Ogiltiga rating värden: {invalid_ratings}"
                )

        # Kontrollera release year
        if "release_year" in df.columns:
            year_stats = df["release_year"].describe()
            validation_results["statistics"]["release_year"] = {
                "min": (
                    float(year_stats["min"]) if pd.notna(year_stats["min"]) else None
                ),
                "max": (
                    float(year_stats["max"]) if pd.notna(year_stats["max"]) else None
                ),
                "mean": (
                    float(year_stats["mean"]) if pd.notna(year_stats["mean"]) else None
                ),
            }

            # Kontrollera för framtida år
            current_year = pd.Timestamp.now().year
            future_years = df[df["release_year"] > current_year + 5].shape[0]
            if future_years > 0:
                validation_results["issues"].append(
                    f"Spel med release år > {current_year + 5}: {future_years}"
                )

        # Kontrollera genre distribution
        if "genres" in df.columns:
            all_genres = set()
            games_without_genres = 0
            for genres in df["genres"]:
                if isinstance(genres, str):
                    # Parse string like "[5, 32]" to list
                    try:
                        import ast

                        genres_list = ast.literal_eval(genres)
                        all_genres.update(genres_list)
                        if len(genres_list) == 0:
                            games_without_genres += 1
                    except:
                        games_without_genres += 1
                elif isinstance(genres, list):
                    all_genres.update(genres)
                    if len(genres) == 0:
                        games_without_genres += 1
                else:
                    games_without_genres += 1

            validation_results["statistics"]["genres"] = {
                "unique_genres": int(len(all_genres)),
                "games_without_genres": int(games_without_genres),
            }

        # Kontrollera theme distribution
        if "themes" in df.columns:
            all_themes = set()
            games_without_themes = 0
            for themes in df["themes"]:
                if isinstance(themes, str):
                    try:
                        import ast

                        themes_list = ast.literal_eval(themes)
                        all_themes.update(themes_list)
                        if len(themes_list) == 0:
                            games_without_themes += 1
                    except:
                        games_without_themes += 1
                elif isinstance(themes, list):
                    all_themes.update(themes)
                    if len(themes) == 0:
                        games_without_themes += 1
                else:
                    games_without_themes += 1

            validation_results["statistics"]["themes"] = {
                "unique_themes": int(len(all_themes)),
                "games_without_themes": int(games_without_themes),
            }

        # Kontrollera platform distribution
        if "platforms" in df.columns:
            all_platforms = set()
            games_without_platforms = 0
            for platforms in df["platforms"]:
                if isinstance(platforms, str):
                    try:
                        import ast

                        platforms_list = ast.literal_eval(platforms)
                        all_platforms.update(platforms_list)
                        if len(platforms_list) == 0:
                            games_without_platforms += 1
                    except:
                        games_without_platforms += 1
                elif isinstance(platforms, list):
                    all_platforms.update(platforms)
                    if len(platforms) == 0:
                        games_without_platforms += 1
                else:
                    games_without_platforms += 1

            validation_results["statistics"]["platforms"] = {
                "unique_platforms": int(len(all_platforms)),
                "games_without_platforms": int(games_without_platforms),
            }

        logger.info(f"Validation klar. Issues: {len(validation_results['issues'])}")
        return validation_results

    def validate_feature_consistency(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Validerar feature consistency

        Args:
            df: DataFrame med speldata

        Returns:
            Dictionary med feature validation results
        """
        logger.info("Validerar feature consistency")

        feature_results = {
            "validation_passed": True,
            "issues": [],
            "genre_features": {},
            "theme_features": {},
            "platform_features": {},
        }

        # Kontrollera genre features
        genre_features = [col for col in df.columns if col.startswith("genre_")]
        if genre_features:
            genre_sum = df[genre_features].sum(axis=1)
            games_without_genres = (genre_sum == 0).sum()
            feature_results["genre_features"] = {
                "total_features": int(len(genre_features)),
                "games_without_genres": int(games_without_genres),
                "feature_names": genre_features,
            }

        # Kontrollera theme features
        theme_features = [col for col in df.columns if col.startswith("theme_")]
        if theme_features:
            theme_sum = df[theme_features].sum(axis=1)
            games_without_themes = (theme_sum == 0).sum()
            feature_results["theme_features"] = {
                "total_features": int(len(theme_features)),
                "games_without_themes": int(games_without_themes),
                "feature_names": theme_features,
            }

        # Kontrollera platform features
        platform_features = [col for col in df.columns if col.startswith("platform_")]
        if platform_features:
            platform_sum = df[platform_features].sum(axis=1)
            games_without_platforms = (platform_sum == 0).sum()
            feature_results["platform_features"] = {
                "total_features": int(len(platform_features)),
                "games_without_platforms": int(games_without_platforms),
                "feature_names": platform_features,
            }

        logger.info("Feature consistency validation klar")
        return feature_results

    def generate_data_report(self, df: pd.DataFrame) -> str:
        """
        Genererar data quality report

        Args:
            df: DataFrame med speldata

        Returns:
            Formaterad rapport som string
        """
        logger.info("Genererar data quality report")

        # Validera data
        validation_results = self.validate_games_data(df)
        feature_results = self.validate_feature_consistency(df)

        # Generera rapport
        report = []
        report.append("=" * 60)
        report.append("IGDB DATA QUALITY REPORT")
        report.append("=" * 60)
        report.append(f"Total spel: {validation_results['total_games']}")
        report.append(
            f"Validation status: {'PASSED' if validation_results['validation_passed'] else 'FAILED'}"
        )
        report.append("")

        # Issues
        if validation_results["issues"]:
            report.append("ISSUES:")
            for issue in validation_results["issues"]:
                report.append(f"  - {issue}")
            report.append("")

        # Statistics
        if validation_results["statistics"]:
            report.append("STATISTICS:")
            for category, stats in validation_results["statistics"].items():
                report.append(f"  {category.upper()}:")
                for key, value in stats.items():
                    if isinstance(value, float):
                        report.append(f"    {key}: {value:.2f}")
                    else:
                        report.append(f"    {key}: {value}")
            report.append("")

        # Feature stats
        if feature_results:
            report.append("FEATURE STATISTICS:")
            for category, stats in feature_results.items():
                if isinstance(stats, dict) and category.endswith("_features"):
                    report.append(f"  {category.upper()}:")
                    for key, value in stats.items():
                        if key == "feature_names":
                            report.append(f"    {key}: {len(value)} features")
                            # Visa första 5 feature-namn som exempel
                            sample_names = value[:5]
                            report.append(f"      Sample: {', '.join(sample_names)}")
                        else:
                            report.append(f"    {key}: {value}")
            report.append("")

        # Data types
        report.append("DATA TYPES:")
        for col, dtype in df.dtypes.items():
            report.append(f"  {col}: {dtype}")

        report.append("=" * 60)

        return "\n".join(report)

    def save_validation_report(self, df: pd.DataFrame, timestamp: str = None) -> str:
        """
        Sparar validation report till fil

        Args:
            df: DataFrame med speldata
            timestamp: Tidsstämpel för filnamn

        Returns:
            Sökväg till sparad rapport
        """
        if timestamp is None:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")

        report = self.generate_data_report(df)
        report_file = self.processed_dir / f"validation_report_{timestamp}.txt"

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        logger.info(f"Validation report sparad till {report_file}")
        return str(report_file)


def main():
    """Huvudfunktion för data validation"""
    validator = IGDBDataValidator()

    # Ladda processad data
    processed_files = list(validator.processed_dir.glob("games_*.csv"))
    if not processed_files:
        print("Ingen processad data hittades")
        return

    # Ta senaste filen
    latest_file = max(processed_files, key=lambda x: x.stat().st_mtime)
    df = pd.read_csv(latest_file)

    print(f"Validerar data från {latest_file}")
    report_file = validator.save_validation_report(df)
    print(f"Rapport sparad till {report_file}")


if __name__ == "__main__":
    main()
