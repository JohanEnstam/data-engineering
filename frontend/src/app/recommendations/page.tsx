"use client";

import { GameSearch } from "@/components/game-search";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Gamepad2, Search, Sparkles } from "lucide-react";

export default function RecommendationsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-4">
            <div className="p-3 bg-blue-100 rounded-full">
              <Gamepad2 className="h-8 w-8 text-blue-600" />
            </div>
          </div>
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Spelrekommendationer
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Sök efter ett spel och upptäck liknande spel baserat på vår ML-modell
          </p>
        </div>

        {/* Search Interface */}
        <div className="flex justify-center mb-8">
          <Card className="w-full max-w-4xl shadow-xl">
            <CardHeader className="text-center pb-4">
              <CardTitle className="flex items-center justify-center gap-2 text-2xl">
                <Search className="h-6 w-6 text-blue-600" />
                Sök efter ett spel
              </CardTitle>
              <CardDescription className="text-lg">
                Börja skriva för att se förslag, välj ett spel för att få rekommendationer
              </CardDescription>
            </CardHeader>
            <CardContent className="p-6">
              <GameSearch />
            </CardContent>
          </Card>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          <Card className="text-center">
            <CardContent className="p-6">
              <div className="p-3 bg-green-100 rounded-full w-fit mx-auto mb-4">
                <Search className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Smart Sökning</h3>
              <p className="text-gray-600">
                Sök efter spelnamn och få omedelbara förslag med cover-bilder
              </p>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardContent className="p-6">
              <div className="p-3 bg-purple-100 rounded-full w-fit mx-auto mb-4">
                <Sparkles className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">ML-Rekommendationer</h3>
              <p className="text-gray-600">
                Få de 3 mest liknande spelen baserat på vår content-based filtering modell
              </p>
            </CardContent>
          </Card>

          <Card className="text-center">
            <CardContent className="p-6">
              <div className="p-3 bg-orange-100 rounded-full w-fit mx-auto mb-4">
                <Gamepad2 className="h-6 w-6 text-orange-600" />
              </div>
              <h3 className="font-semibold text-lg mb-2">100+ Spel</h3>
              <p className="text-gray-600">
                Utforska vår databas med spel från IGDB API med 84 ML-features
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 text-gray-500">
          <p>Powered by IGDB API och Machine Learning</p>
        </div>
      </div>
    </div>
  );
}
