"use client";

import { useState, useEffect, useRef } from "react";
import { Search, Gamepad2, Star } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface Game {
  id: number;
  name: string;
  rating?: number;
  genres?: string;
  themes?: string;
  platforms?: string;
  cover_url?: string;
  similarity_score?: number;
}

interface GameSearchProps {
  onGameSelect?: (game: Game) => void;
}

export function GameSearch({ onGameSelect }: GameSearchProps) {
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<Game[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  const [recommendations, setRecommendations] = useState<Game[]>([]);
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false);
  
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Debounced search
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (query.length < 2) {
      setSearchResults([]);
      setShowResults(false);
      return;
    }

    searchTimeoutRef.current = setTimeout(async () => {
      setIsSearching(true);
      try {
        const response = await fetch(`http://localhost:8000/api/recommendations/search?q=${encodeURIComponent(query)}&limit=8`);
        if (response.ok) {
          const results = await response.json();
          setSearchResults(results);
          setShowResults(true);
        }
      } catch (error) {
        console.error("Search error:", error);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [query]);

  // Load recommendations when game is selected
  useEffect(() => {
    if (selectedGame) {
      loadRecommendations(selectedGame.id);
    }
  }, [selectedGame]);

  const loadRecommendations = async (gameId: number) => {
    setIsLoadingRecommendations(true);
    try {
      const response = await fetch(`http://localhost:8000/api/recommendations/recommendations/${gameId}?limit=3`);
      if (response.ok) {
        const recs = await response.json();
        setRecommendations(recs);
      }
    } catch (error) {
      console.error("Recommendations error:", error);
    } finally {
      setIsLoadingRecommendations(false);
    }
  };

  const handleGameSelect = (game: Game) => {
    setSelectedGame(game);
    setQuery(game.name);
    setShowResults(false);
    onGameSelect?.(game);
  };

  const handleClear = () => {
    setQuery("");
    setSelectedGame(null);
    setRecommendations([]);
    setSearchResults([]);
    setShowResults(false);
    inputRef.current?.focus();
  };

  const formatGenres = (genres: string) => {
    if (!genres) return [];
    try {
      const genreIds = JSON.parse(genres);
      return Array.isArray(genreIds) ? genreIds.slice(0, 3) : [];
    } catch {
      return [];
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Main Search Interface */}
      <div className="relative">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
          <Input
            ref={inputRef}
            type="text"
            placeholder="Sök efter ett spel..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => query.length >= 2 && setShowResults(true)}
            className="pl-12 pr-12 h-14 text-lg border-2 border-gray-200 focus:border-blue-500 rounded-xl"
          />
          {query && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleClear}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 h-8 w-8 p-0"
            >
              ×
            </Button>
          )}
        </div>

        {/* Search Results Dropdown */}
        {showResults && searchResults.length > 0 && (
          <Card className="absolute top-full left-0 right-0 mt-2 z-50 max-h-96 overflow-y-auto">
            <CardContent className="p-0">
              {searchResults.map((game) => (
                <div
                  key={game.id}
                  onClick={() => handleGameSelect(game)}
                  className="flex items-center space-x-3 p-3 hover:bg-gray-50 cursor-pointer border-b last:border-b-0"
                >
                  <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center">
                    {game.cover_url ? (
                      <img
                        src={game.cover_url}
                        alt={game.name}
                        className="w-full h-full object-cover rounded-lg"
                      />
                    ) : (
                      <Gamepad2 className="h-6 w-6 text-gray-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-gray-900 truncate">{game.name}</h3>
                    {game.rating && (
                      <div className="flex items-center space-x-1 text-sm text-gray-500">
                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        <span>{game.rating}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Loading State */}
        {isSearching && (
          <Card className="absolute top-full left-0 right-0 mt-2 z-50">
            <CardContent className="p-4 text-center text-gray-500">
              Söker...
            </CardContent>
          </Card>
        )}
      </div>

      {/* Selected Game & Recommendations */}
      {selectedGame && (
        <div className="space-y-6">
          {/* Selected Game */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-start space-x-4">
                <div className="w-20 h-20 bg-gray-200 rounded-lg flex items-center justify-center">
                  {selectedGame.cover_url ? (
                    <img
                      src={selectedGame.cover_url}
                      alt={selectedGame.name}
                      className="w-full h-full object-cover rounded-lg"
                    />
                  ) : (
                    <Gamepad2 className="h-8 w-8 text-gray-400" />
                  )}
                </div>
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-gray-900">{selectedGame.name}</h2>
                  {selectedGame.rating && (
                    <div className="flex items-center space-x-1 mt-1">
                      <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                      <span className="text-lg font-medium">{selectedGame.rating}</span>
                    </div>
                  )}
                  <div className="flex flex-wrap gap-2 mt-3">
                    {formatGenres(selectedGame.genres || "").map((genre, index) => (
                      <Badge key={index} variant="secondary">
                        Genre {genre}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Liknande spel
            </h3>
            
            {isLoadingRecommendations ? (
              <div className="text-center py-8 text-gray-500">
                Laddar rekommendationer...
              </div>
            ) : recommendations.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {recommendations.map((rec) => (
                  <Card key={rec.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        <div className="w-full h-32 bg-gray-200 rounded-lg flex items-center justify-center">
                          {rec.cover_url ? (
                            <img
                              src={rec.cover_url}
                              alt={rec.name}
                              className="w-full h-full object-cover rounded-lg"
                            />
                          ) : (
                            <Gamepad2 className="h-8 w-8 text-gray-400" />
                          )}
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900 truncate">{rec.name}</h4>
                          {rec.rating && (
                            <div className="flex items-center space-x-1 mt-1">
                              <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                              <span className="text-sm">{rec.rating}</span>
                            </div>
                          )}
                          {rec.similarity_score && (
                            <div className="text-xs text-gray-500 mt-1">
                              Likhet: {(rec.similarity_score * 100).toFixed(1)}%
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                Inga rekommendationer hittades
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
