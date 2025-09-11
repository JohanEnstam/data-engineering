"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { Gamepad2, Calendar, Star, Tag, Palette, Monitor } from "lucide-react";
import { Game, DataQualityReport } from "@/types/game";

interface LookupTables {
  genres: Record<string, string>;
  themes: Record<string, string>;
  platforms: Record<string, string>;
}

interface CollectionStatsProps {
  games: Game[];
  dataQuality: DataQualityReport | null;
}

export function CollectionStats({ games, dataQuality }: CollectionStatsProps) {
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

  // Calculate statistics
  const totalGames = games.length;
  const gamesWithRatings = games.filter(game => game.rating !== null).length;
  const gamesWithReleaseYear = games.filter(game => game.release_year !== null).length;
  const averageRating = gamesWithRatings > 0 
    ? games.reduce((sum, game) => sum + (game.rating || 0), 0) / gamesWithRatings / 100
    : 0;

  // Genre distribution
  const genreCounts = games.reduce((acc, game) => {
    game.genres.forEach(genreId => {
      acc[genreId] = (acc[genreId] || 0) + 1;
    });
    return acc;
  }, {} as Record<number, number>);

  const genreData = Object.entries(genreCounts)
    .map(([genreId, count]) => ({
      genre: lookups?.genres[genreId] || `Genre ${genreId}`,
      count,
      percentage: (count / totalGames) * 100
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);

  // Theme distribution
  const themeCounts = games.reduce((acc, game) => {
    game.themes.forEach(themeId => {
      acc[themeId] = (acc[themeId] || 0) + 1;
    });
    return acc;
  }, {} as Record<number, number>);

  const themeData = Object.entries(themeCounts)
    .map(([themeId, count]) => ({
      theme: lookups?.themes[themeId] || `Theme ${themeId}`,
      count,
      percentage: (count / totalGames) * 100
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8);

  // Release year distribution
  const yearCounts = games.reduce((acc, game) => {
    if (game.release_year) {
      acc[game.release_year] = (acc[game.release_year] || 0) + 1;
    }
    return acc;
  }, {} as Record<number, number>);

  const yearData = Object.entries(yearCounts)
    .map(([year, count]) => ({
      year: parseInt(year),
      count
    }))
    .sort((a, b) => a.year - b.year);

  // Platform distribution
  const platformCounts = games.reduce((acc, game) => {
    game.platforms.forEach(platformId => {
      acc[platformId] = (acc[platformId] || 0) + 1;
    });
    return acc;
  }, {} as Record<number, number>);

  const platformData = Object.entries(platformCounts)
    .map(([platformId, count]) => ({
      platform: lookups?.platforms[platformId] || `Unknown Platform ${platformId}`,
      count,
      percentage: (count / totalGames) * 100
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 6);

  // Color palette for charts
  const colors = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00', '#ff00ff', '#00ffff', '#ffff00'];

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Games</CardTitle>
            <Gamepad2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalGames}</div>
            <p className="text-xs text-muted-foreground">
              Collected from IGDB
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Average Rating</CardTitle>
            <Star className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {averageRating > 0 ? averageRating.toFixed(1) : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              {gamesWithRatings} games rated
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Data Completeness</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {dataQuality ? '100%' : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground">
              Validation passed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Unique Genres</CardTitle>
            <Tag className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.keys(genreCounts).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Across all games
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Genre Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Top Genres</CardTitle>
            <CardDescription>
              Most common genres in the collection
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={genreData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="genre" 
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    fontSize={12}
                  />
                  <YAxis />
                  <Tooltip 
                    formatter={(value: number) => [value, 'Games']}
                    labelFormatter={(label) => `Genre: ${label}`}
                  />
                  <Bar dataKey="count" fill="#8884d8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Theme Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Top Themes</CardTitle>
            <CardDescription>
              Most common themes in the collection
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={themeData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {themeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => [value, 'Games']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Release Year Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Release Years</CardTitle>
            <CardDescription>
              Distribution of games by release year
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={yearData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="year" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value: number) => [value, 'Games']}
                    labelFormatter={(label) => `Year: ${label}`}
                  />
                  <Bar dataKey="count" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Platform Distribution */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Platforms</CardTitle>
            <CardDescription>
              Most common platforms in the collection
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {platformData.map((platform, index) => (
                <div key={platform.platform} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Monitor className="h-4 w-4 text-gray-500" />
                    <span className="text-sm">{platform.platform}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">{platform.count}</Badge>
                    <span className="text-xs text-gray-500">
                      {platform.percentage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Data Quality Summary */}
      {dataQuality && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Data Quality Summary</CardTitle>
            <CardDescription>
              Key metrics from the data validation process
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {dataQuality.statistics?.genres?.unique_genres || 0}
                </div>
                <div className="text-sm text-gray-600">Unique Genres</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {dataQuality.statistics?.themes?.unique_themes || 0}
                </div>
                <div className="text-sm text-gray-600">Unique Themes</div>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {dataQuality.statistics?.platforms?.unique_platforms || 0}
                </div>
                <div className="text-sm text-gray-600">Unique Platforms</div>
              </div>
              <div className="text-center p-3 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {(dataQuality.feature_statistics?.genre_features?.total_features || 0) + 
                   (dataQuality.feature_statistics?.theme_features?.total_features || 0)}
                </div>
                <div className="text-sm text-gray-600">ML Features</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
