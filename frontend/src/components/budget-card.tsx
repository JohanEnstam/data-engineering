"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { DollarSign, AlertTriangle, TrendingUp, Server, Database, Brain, HardDrive } from "lucide-react";
import { BudgetInfo } from "@/types/game";

interface BudgetCardProps {
  budgetInfo: BudgetInfo | null;
}

export function BudgetCard({ budgetInfo }: BudgetCardProps) {
  if (!budgetInfo) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            GCP Budget Monitoring
          </CardTitle>
          <CardDescription>
            No budget information available
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-gray-500">
            Connect to GCP to monitor budget usage
          </div>
        </CardContent>
      </Card>
    );
  }

  const usagePercentage = (budgetInfo.used_credits / budgetInfo.total_credits) * 100;
  const remainingCredits = budgetInfo.total_credits - budgetInfo.used_credits;
  const isNearLimit = usagePercentage > 80;
  const isOverLimit = usagePercentage > 100;

  const services = [
    {
      name: "BigQuery",
      cost: budgetInfo.services.bigquery,
      icon: Database,
      description: "Data warehouse and analytics"
    },
    {
      name: "Cloud Run",
      cost: budgetInfo.services.cloud_run,
      icon: Server,
      description: "API and web hosting"
    },
    {
      name: "Vertex AI",
      cost: budgetInfo.services.vertex_ai,
      icon: Brain,
      description: "ML model training and inference"
    },
    {
      name: "Cloud Storage",
      cost: budgetInfo.services.cloud_storage,
      icon: HardDrive,
      description: "Data storage and backup"
    }
  ];

  return (
    <div className="space-y-6">
      {/* Budget Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            Budget Overview
          </CardTitle>
          <CardDescription>
            GCP Credits Usage and Projections
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Usage Progress */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span>Credits Used</span>
              <span className="font-medium">
                ${budgetInfo.used_credits} / ${budgetInfo.total_credits}
              </span>
            </div>
            <Progress 
              value={usagePercentage} 
              className={`h-2 ${isOverLimit ? 'bg-red-500' : isNearLimit ? 'bg-yellow-500' : 'bg-green-500'}`}
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0%</span>
              <span>{usagePercentage.toFixed(1)}%</span>
              <span>100%</span>
            </div>
          </div>

          {/* Status Badge */}
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Status</span>
            <Badge 
              variant={isOverLimit ? "destructive" : isNearLimit ? "secondary" : "default"}
            >
              {isOverLimit ? (
                <div className="flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  Over Budget
                </div>
              ) : isNearLimit ? (
                <div className="flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" />
                  Near Limit
                </div>
              ) : (
                <div className="flex items-center gap-1">
                  <TrendingUp className="h-3 w-3" />
                  Healthy
                </div>
              )}
            </Badge>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                ${remainingCredits}
              </div>
              <div className="text-sm text-gray-600">Remaining Credits</div>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">
                ${budgetInfo.monthly_estimate}
              </div>
              <div className="text-sm text-gray-600">Monthly Estimate</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Service Breakdown */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Service Costs</CardTitle>
          <CardDescription>
            Breakdown of costs by GCP service
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {services.map((service) => {
              const Icon = service.icon;
              const servicePercentage = (service.cost / budgetInfo.total_credits) * 100;
              
              return (
                <div key={service.name} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <Icon className="h-4 w-4 text-gray-500" />
                      <div>
                        <div className="font-medium">{service.name}</div>
                        <div className="text-sm text-gray-500">{service.description}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">${service.cost}</div>
                      <div className="text-sm text-gray-500">{servicePercentage.toFixed(1)}%</div>
                    </div>
                  </div>
                  <Progress value={servicePercentage} className="h-1" />
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Budget Alerts */}
      {(isNearLimit || isOverLimit) && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-700">
              <AlertTriangle className="h-5 w-5" />
              Budget Alert
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-red-700">
              {isOverLimit ? (
                <p>
                  <strong>Warning:</strong> You have exceeded your GCP budget limit. 
                  Consider optimizing your usage or increasing your budget allocation.
                </p>
              ) : (
                <p>
                  <strong>Notice:</strong> You are approaching your budget limit. 
                  Monitor your usage closely to avoid overages.
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Cost Optimization Tips</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <strong>BigQuery:</strong> Use partitioned tables and optimize queries to reduce costs
              </div>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <strong>Cloud Run:</strong> Set up auto-scaling and use appropriate CPU/memory limits
              </div>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <strong>Vertex AI:</strong> Use preemptible instances for training and batch predictions
              </div>
            </div>
            <div className="flex items-start gap-2">
              <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
              <div>
                <strong>Cloud Storage:</strong> Use appropriate storage classes and lifecycle policies
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
