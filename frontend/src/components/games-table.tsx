"use client";

import { useState, useEffect } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Search, Filter, Gamepad2, Calendar, Star } from "lucide-react";
import { Game } from "@/types/game";

interface LookupTables {
  genres: Record<string, string>;
  themes: Record<string, string>;
  platforms: Record<string, string>;
}

interface GamesTableProps {
  games: Game[];
}

export function GamesTable({ games }: GamesTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterGenre, setFilterGenre] = useState<string>("all");
  const [filterTheme, setFilterTheme] = useState<string>("all");
  const [sortBy, setSortBy] = useState<keyof Game>("name");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  const [lookups, setLookups] = useState<LookupTables | null>(null);

  // Load lookup tables
  useEffect(() => {
    const loadLookups = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/lookups');
        if (response.ok) {
          const data = await response.json();
          setLookups(data);
        }
      } catch (error) {
        console.error('Failed to load lookup tables:', error);
      }
    };
    loadLookups();
  }, []);

  // Get unique genres and themes for filtering
  const allGenres = Array.from(new Set(games.flatMap(game => game.genres)));
  const allThemes = Array.from(new Set(games.flatMap(game => game.themes)));

  // Filter and sort games
  const filteredGames = games
    .filter(game => {
      const matchesSearch = game.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           game.summary.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesGenre = filterGenre === "all" || game.genres.includes(parseInt(filterGenre));
      const matchesTheme = filterTheme === "all" || game.themes.includes(parseInt(filterTheme));
      
      return matchesSearch && matchesGenre && matchesTheme;
    })
    .sort((a, b) => {
      const aValue = a[sortBy];
      const bValue = b[sortBy];
      
      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortOrder === 'asc' 
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      return 0;
    });

  const handleSort = (column: keyof Game) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  const formatRating = (rating: number | null) => {
    if (!rating) return 'N/A';
    return (rating / 100).toFixed(1);
  };

  return (
    <div className="space-y-4">
      {/* Search and Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            placeholder="Search games..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        
        <div className="flex gap-2">
          <select
            value={filterGenre}
            onChange={(e) => setFilterGenre(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="all">All Genres</option>
            {allGenres.map(genreId => (
              <option key={genreId} value={genreId.toString()}>
                {lookups?.genres[genreId.toString()] || `Genre ${genreId}`}
              </option>
            ))}
          </select>
          
          <select
            value={filterTheme}
            onChange={(e) => setFilterTheme(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm"
          >
            <option value="all">All Themes</option>
            {allThemes.map(themeId => (
              <option key={themeId} value={themeId.toString()}>
                {lookups?.themes[themeId.toString()] || `Theme ${themeId}`}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Results Count */}
      <div className="text-sm text-gray-600">
        Showing {filteredGames.length} of {games.length} games
      </div>

      {/* Games Table */}
      <div className="border rounded-lg">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead 
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort('name')}
              >
                <div className="flex items-center gap-2">
                  Name
                  {sortBy === 'name' && (
                    <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </TableHead>
              <TableHead>Summary</TableHead>
              <TableHead 
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort('rating')}
              >
                <div className="flex items-center gap-2">
                  Rating
                  {sortBy === 'rating' && (
                    <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </TableHead>
              <TableHead 
                className="cursor-pointer hover:bg-gray-50"
                onClick={() => handleSort('release_year')}
              >
                <div className="flex items-center gap-2">
                  Year
                  {sortBy === 'release_year' && (
                    <span className="text-xs">{sortOrder === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </TableHead>
              <TableHead>Genres</TableHead>
              <TableHead>Themes</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredGames.map((game) => (
              <TableRow key={game.id}>
                <TableCell className="font-medium">
                  <div className="flex items-center gap-2">
                    <Gamepad2 className="h-4 w-4 text-gray-400" />
                    {game.name}
                  </div>
                </TableCell>
                <TableCell className="max-w-xs">
                  <div className="truncate" title={game.summary}>
                    {game.summary || 'No summary available'}
                  </div>
                </TableCell>
                <TableCell>
                  {game.rating ? (
                    <div className="flex items-center gap-1">
                      <Star className="h-4 w-4 text-yellow-400 fill-current" />
                      {formatRating(game.rating)}
                    </div>
                  ) : (
                    'N/A'
                  )}
                </TableCell>
                <TableCell>
                  {game.release_year ? (
                    <div className="flex items-center gap-1">
                      <Calendar className="h-4 w-4 text-gray-400" />
                      {game.release_year}
                    </div>
                  ) : (
                    'N/A'
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {game.genres.slice(0, 3).map((genreId) => (
                      <Badge key={genreId} variant="secondary" className="text-xs">
                        {lookups?.genres[genreId.toString()] || genreId}
                      </Badge>
                    ))}
                    {game.genres.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{game.genres.length - 3}
                      </Badge>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex flex-wrap gap-1">
                    {game.themes.slice(0, 2).map((themeId) => (
                      <Badge key={themeId} variant="outline" className="text-xs">
                        {lookups?.themes[themeId.toString()] || themeId}
                      </Badge>
                    ))}
                    {game.themes.length > 2 && (
                      <Badge variant="outline" className="text-xs">
                        +{game.themes.length - 2}
                      </Badge>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {filteredGames.length === 0 && (
        <Card>
          <CardContent className="text-center py-8">
            <Gamepad2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <CardTitle className="text-lg mb-2">No games found</CardTitle>
            <CardDescription>
              Try adjusting your search terms or filters
            </CardDescription>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
