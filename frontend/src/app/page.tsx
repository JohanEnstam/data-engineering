"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { AlertCircle, Gamepad2, TrendingUp, DollarSign, Database } from "lucide-react";
import { Game, DataQualityReport, BudgetInfo } from "@/types/game";
import { GamesTable } from "@/components/games-table";
import { DataQualityCard } from "@/components/data-quality-card";
import { BudgetCard } from "@/components/budget-card";
import { BudgetDashboard } from "@/components/budget-dashboard";
import { CollectionStats } from "@/components/collection-stats";

export default function Dashboard() {
  const [games, setGames] = useState<Game[]>([]);
  const [dataQuality, setDataQuality] = useState<DataQualityReport | null>(null);
  const [budgetInfo, setBudgetInfo] = useState<BudgetInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load games data
      const gamesResponse = await fetch('http://localhost:8000/api/games');
      if (gamesResponse.ok) {
        const gamesData = await gamesResponse.json();
        setGames(gamesData);
      } else {
        setGames([]);
        setError('Failed to load games data');
      }

      // Load data quality report
      const qualityResponse = await fetch('http://localhost:8000/api/data-quality');
      if (qualityResponse.ok) {
        const qualityData = await qualityResponse.json();
        setDataQuality(qualityData);
      } else {
        setDataQuality(null);
      }

      // Load budget info
      const budgetResponse = await fetch('http://localhost:8000/api/budget');
      if (budgetResponse.ok) {
        const budgetData = await budgetResponse.json();
        setBudgetInfo(budgetData);
      } else {
        setBudgetInfo(null);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setGames([]);
      setDataQuality(null);
      setBudgetInfo(null);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-lg">Loading game data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              Error
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-600">{error}</p>
            <button 
              onClick={loadData}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Try Again
            </button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Empty state when no games are loaded
  if (games.length === 0 && !loading && !error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="w-96">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-gray-600">
              <Gamepad2 className="h-5 w-5" />
              No Games Found
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              No games data is available. This could mean:
            </p>
            <ul className="text-sm text-gray-500 mb-4 space-y-1">
              <li>• Data collection hasn&apos;t been run yet</li>
              <li>• No games were found in the last collection</li>
              <li>• Data processing failed</li>
            </ul>
            <button 
              onClick={loadData}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Refresh Data
            </button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Games</CardTitle>
              <Gamepad2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{games.length}</div>
              <p className="text-xs text-muted-foreground">
                From IGDB API
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Data Quality</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {dataQuality?.validation_status === 'PASSED' ? '100%' : 'N/A'}
              </div>
              <p className="text-xs text-muted-foreground">
                Validation Status
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Budget Used</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {budgetInfo ? `${budgetInfo.used_credits}/${budgetInfo.total_credits}` : 'N/A'}
              </div>
              <p className="text-xs text-muted-foreground">
                GCP Credits
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">ML Features</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {dataQuality?.feature_statistics.genre_features.total_features || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                Genre Features
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="games" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="games">Games</TabsTrigger>
            <TabsTrigger value="quality">Data Quality</TabsTrigger>
            <TabsTrigger value="budget">Budget</TabsTrigger>
            <TabsTrigger value="stats">Statistics</TabsTrigger>
          </TabsList>

          <TabsContent value="games" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Game Collection</CardTitle>
                <CardDescription>
                  Browse and explore the collected game data from IGDB API
                </CardDescription>
              </CardHeader>
              <CardContent>
                <GamesTable games={games} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="quality" className="space-y-6">
            <DataQualityCard dataQuality={dataQuality} />
          </TabsContent>

          <TabsContent value="budget" className="space-y-6">
            <BudgetDashboard />
          </TabsContent>

          <TabsContent value="stats" className="space-y-6">
            <CollectionStats games={games} dataQuality={dataQuality} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}