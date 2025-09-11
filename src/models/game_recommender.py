"""
Game Recommendation Model
Content-based filtering för spelrekommendationer
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GameRecommender:
    """Content-based filtering för spelrekommendationer"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.processed_dir = self.data_dir / "processed"
        self.models_dir = self.data_dir / "models"

        # Skapa models mapp om den inte finns
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Modell komponenter
        self.games_df = None
        self.feature_matrix = None
        self.similarity_matrix = None
        self.tfidf_vectorizer = None
        self.scaler = None

    def load_data(self) -> bool:
        """Laddar processad speldata"""
        try:
            # Hitta senaste processade fil
            csv_files = list(self.processed_dir.glob("games_*.csv"))
            if not csv_files:
                logger.error("Ingen processad data hittades")
                return False

            latest_file = max(csv_files, key=lambda x: x.stat().st_mtime)
            self.games_df = pd.read_csv(latest_file)

            logger.info(f"Laddade {len(self.games_df)} spel från {latest_file}")
            return True

        except Exception as e:
            logger.error(f"Fel vid laddning av data: {e}")
            return False

    def prepare_features(self) -> bool:
        """Förbereder features för ML-modell"""
        try:
            logger.info("Förbereder features för ML-modell")

            # Hitta feature kolumner (genre_, theme_, platform_)
            feature_columns = [
                col
                for col in self.games_df.columns
                if col.startswith(("genre_", "theme_", "platform_"))
            ]

            logger.info(f"Hittade {len(feature_columns)} feature kolumner")

            # Skapa feature matrix
            self.feature_matrix = self.games_df[feature_columns].fillna(0).astype(float)

            # Lägg till text features (summary + storyline)
            text_features = []
            for _, game in self.games_df.iterrows():
                summary = str(game.get("summary", ""))
                storyline = str(game.get("storyline", ""))
                text = f"{summary} {storyline}".strip()
                text_features.append(text)

            # TF-IDF för text features
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=100, stop_words="english", ngram_range=(1, 2)
            )

            tfidf_matrix = self.tfidf_vectorizer.fit_transform(text_features)

            # Kombinera features
            from scipy.sparse import hstack

            self.feature_matrix = hstack(
                [self.feature_matrix.values, tfidf_matrix]
            ).toarray()

            # Normalisera features
            self.scaler = StandardScaler()
            self.feature_matrix = self.scaler.fit_transform(self.feature_matrix)

            logger.info(f"Feature matrix shape: {self.feature_matrix.shape}")
            return True

        except Exception as e:
            logger.error(f"Fel vid förberedelse av features: {e}")
            return False

    def train_model(self) -> bool:
        """Tränar rekommendationsmodellen"""
        try:
            logger.info("Tränar rekommendationsmodellen")

            # Beräkna cosine similarity
            self.similarity_matrix = cosine_similarity(self.feature_matrix)

            logger.info(f"Similarity matrix shape: {self.similarity_matrix.shape}")
            return True

        except Exception as e:
            logger.error(f"Fel vid träning av modell: {e}")
            return False

    def get_recommendations(
        self, game_id: int, n_recommendations: int = 5
    ) -> List[Dict]:
        """
        Får rekommendationer för ett specifikt spel

        Args:
            game_id: ID för spelet att få rekommendationer för
            n_recommendations: Antal rekommendationer att returnera

        Returns:
            Lista med rekommendationer
        """
        try:
            # Hitta spel index
            game_idx = self.games_df[self.games_df["id"] == game_id].index
            if len(game_idx) == 0:
                logger.warning(f"Spel med ID {game_id} hittades inte")
                return []

            game_idx = game_idx[0]

            # Hitta mest liknande spel
            similarity_scores = self.similarity_matrix[game_idx]

            # Sortera efter similarity (högst först)
            similar_indices = np.argsort(similarity_scores)[::-1]

            # Exkludera själva spelet och ta top N
            similar_indices = similar_indices[similar_indices != game_idx][
                :n_recommendations
            ]

            # Skapa rekommendationer
            recommendations = []
            for idx in similar_indices:
                game = self.games_df.iloc[idx]
                recommendations.append(
                    {
                        "id": int(game["id"]),
                        "name": game["name"],
                        "rating": game.get("rating", 0),
                        "genres": game.get("genres", ""),
                        "themes": game.get("themes", ""),
                        "platforms": game.get("platforms", ""),
                        "similarity_score": float(similarity_scores[idx]),
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"Fel vid rekommendation: {e}")
            return []

    def search_games(self, query: str, n_results: int = 10) -> List[Dict]:
        """
        Söker efter spel baserat på namn

        Args:
            query: Sökterm
            n_results: Antal resultat att returnera

        Returns:
            Lista med sökresultat
        """
        try:
            # Filtrera spel baserat på namn
            mask = self.games_df["name"].str.contains(query, case=False, na=False)
            results = self.games_df[mask].head(n_results)

            search_results = []
            for _, game in results.iterrows():
                search_results.append(
                    {
                        "id": int(game["id"]),
                        "name": game["name"],
                        "rating": game.get("rating", 0),
                        "genres": game.get("genres", ""),
                        "themes": game.get("themes", ""),
                        "platforms": game.get("platforms", ""),
                    }
                )

            return search_results

        except Exception as e:
            logger.error(f"Fel vid sökning: {e}")
            return []

    def save_model(self, filename: str = None) -> bool:
        """Sparar tränad modell"""
        try:
            if filename is None:
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"game_recommender_{timestamp}.pkl"

            model_path = self.models_dir / filename

            model_data = {
                "games_df": self.games_df,
                "feature_matrix": self.feature_matrix,
                "similarity_matrix": self.similarity_matrix,
                "tfidf_vectorizer": self.tfidf_vectorizer,
                "scaler": self.scaler,
            }

            with open(model_path, "wb") as f:
                pickle.dump(model_data, f)

            logger.info(f"Modell sparad till {model_path}")
            return True

        except Exception as e:
            logger.error(f"Fel vid sparning av modell: {e}")
            return False

    def load_model(self, filename: str) -> bool:
        """Laddar tränad modell"""
        try:
            model_path = self.models_dir / filename

            with open(model_path, "rb") as f:
                model_data = pickle.load(f)

            self.games_df = model_data["games_df"]
            self.feature_matrix = model_data["feature_matrix"]
            self.similarity_matrix = model_data["similarity_matrix"]
            self.tfidf_vectorizer = model_data["tfidf_vectorizer"]
            self.scaler = model_data["scaler"]

            logger.info(f"Modell laddad från {model_path}")
            return True

        except Exception as e:
            logger.error(f"Fel vid laddning av modell: {e}")
            return False

    def train_full_pipeline(self) -> bool:
        """Kör hela träningspipeline"""
        try:
            logger.info("Börjar fullständig träningspipeline")

            # Ladda data
            if not self.load_data():
                return False

            # Förbered features
            if not self.prepare_features():
                return False

            # Träna modell
            if not self.train_model():
                return False

            # Spara modell
            if not self.save_model():
                return False

            logger.info("Träningspipeline klar!")
            return True

        except Exception as e:
            logger.error(f"Fel i träningspipeline: {e}")
            return False


def main():
    """Testa rekommendationsmodellen"""
    recommender = GameRecommender()

    # Träna modell
    if recommender.train_full_pipeline():
        logger.info("Modell tränad framgångsrikt!")

        # Testa rekommendationer
        if len(recommender.games_df) > 0:
            test_game_id = recommender.games_df.iloc[0]["id"]
            recommendations = recommender.get_recommendations(test_game_id, 5)

            logger.info(f"Rekommendationer för {recommender.games_df.iloc[0]['name']}:")
            for i, rec in enumerate(recommendations, 1):
                logger.info(
                    f"{i}. {rec['name']} (similarity: {rec['similarity_score']:.3f})"
                )

        # Testa sökning
        search_results = recommender.search_games("super", 3)
        logger.info(f"Sökresultat för 'super': {len(search_results)} spel")
        for result in search_results:
            logger.info(f"- {result['name']}")

    else:
        logger.error("Träning misslyckades")


if __name__ == "__main__":
    main()
