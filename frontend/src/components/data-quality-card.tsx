"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { AlertCircle, CheckCircle, Database, BarChart3 } from "lucide-react";
import { DataQualityReport } from "@/types/game";

interface DataQualityCardProps {
  dataQuality: DataQualityReport | null;
}

export function DataQualityCard({ dataQuality }: DataQualityCardProps) {
  if (!dataQuality) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Data Quality Report
          </CardTitle>
          <CardDescription>
            No data quality information available
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            Run data collection to generate quality report
          </div>
        </CardContent>
      </Card>
    );
  }

  const isPassed = dataQuality.validation_status === 'PASSED';
  const issuesCount = dataQuality.issues.length;

  return (
    <div className="space-y-6">
      {/* Overall Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Data Quality Overview
          </CardTitle>
          <CardDescription>
            Validation status and key metrics
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Validation Status</span>
            <Badge variant={isPassed ? "default" : "destructive"}>
              {isPassed ? (
                <div className="flex items-center gap-1">
                  <CheckCircle className="h-3 w-3" />
                  {dataQuality.validation_status}
                </div>
              ) : (
                <div className="flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  {dataQuality.validation_status}
                </div>
              )}
            </Badge>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Total Games</span>
              <span className="font-medium">{dataQuality.total_games}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span>Issues Found</span>
              <span className="font-medium">{issuesCount}</span>
            </div>
          </div>

          {issuesCount > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-red-600">Issues:</h4>
              <ul className="text-sm text-red-600 space-y-1">
                {dataQuality.issues.map((issue, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <AlertCircle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    {issue}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Rating Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Rating Statistics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Min Rating</span>
                <span>{dataQuality.statistics.rating.min?.toFixed(1) || 'N/A'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Max Rating</span>
                <span>{dataQuality.statistics.rating.max?.toFixed(1) || 'N/A'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Mean Rating</span>
                <span>{dataQuality.statistics.rating.mean?.toFixed(1) || 'N/A'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Std Deviation</span>
                <span>{dataQuality.statistics.rating.std?.toFixed(1) || 'N/A'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Release Year Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Release Year Statistics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Earliest Year</span>
                <span>{dataQuality.statistics.release_year.min || 'N/A'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Latest Year</span>
                <span>{dataQuality.statistics.release_year.max || 'N/A'}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Average Year</span>
                <span>{dataQuality.statistics.release_year.mean?.toFixed(0) || 'N/A'}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Genre Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Genre Statistics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Unique Genres</span>
                <span className="font-medium">{dataQuality.statistics.genres.unique_genres}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Games without Genres</span>
                <span className="font-medium">{dataQuality.statistics.genres.games_without_genres}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Genre Features</span>
                <span className="font-medium">{dataQuality.feature_statistics.genre_features.total_features}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Theme Statistics */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Theme Statistics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Unique Themes</span>
                <span className="font-medium">{dataQuality.statistics.themes.unique_themes}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Games without Themes</span>
                <span className="font-medium">{dataQuality.statistics.themes.games_without_themes}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Theme Features</span>
                <span className="font-medium">{dataQuality.feature_statistics.theme_features.total_features}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Platform Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Platform Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold">{dataQuality.statistics.platforms.unique_platforms}</div>
              <div className="text-sm text-gray-600">Unique Platforms</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{dataQuality.statistics.platforms.games_without_platforms}</div>
              <div className="text-sm text-gray-600">Games without Platforms</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">{dataQuality.feature_statistics.platform_features.total_features}</div>
              <div className="text-sm text-gray-600">Platform Features</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold">
                {dataQuality.feature_statistics.platform_features.games_without_platforms}
              </div>
              <div className="text-sm text-gray-600">Missing Platform Data</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
