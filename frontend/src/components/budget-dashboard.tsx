"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Progress } from "../components/ui/progress";
import { Badge } from "../components/ui/badge";
import { Button } from "../components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { 
  DollarSign, 
  AlertTriangle, 
  TrendingUp, 
  Server, 
  Database, 
  Brain, 
  HardDrive,
  RefreshCw,
  Activity,
  Calendar,
  Target
} from "lucide-react";

// Types for GCP Budget API responses
interface BudgetInfo {
  project_id: string;
  project_name: string;
  project_number: string;
  billing_account_id: string | null;
  monthly_budget_limit: number;
  current_month_cost: number;
  budget_utilization_percent: number;
  days_remaining_in_month: number;
  projected_monthly_cost: number;
  is_over_budget: boolean;
  is_approaching_limit: boolean;
  last_updated: string;
}

interface CostAlert {
  alert_type: string;
  message: string;
  severity: string;
  current_cost: number;
  threshold: number;
  timestamp: string;
}

interface ResourceUsage {
  compute_instances: number;
  storage_gb: number;
  api_requests: number;
  data_processed_gb: number;
  last_updated: string;
}

interface BudgetSummary {
  budget_info: BudgetInfo;
  alerts: CostAlert[];
  resource_usage: ResourceUsage;
  status: string;
}

interface BudgetDashboardProps {
  className?: string;
}

export function BudgetDashboard({ className }: BudgetDashboardProps) {
  const [budgetSummary, setBudgetSummary] = useState<BudgetSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);

  const fetchBudgetData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:8000/api/budget/summary?budget_limit=100');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setBudgetSummary(data);
      setLastRefresh(new Date());
    } catch (err) {
      console.error('Error fetching budget data:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch budget data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBudgetData();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(fetchBudgetData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical': return 'destructive';
      case 'warning': return 'secondary';
      case 'healthy': return 'default';
      default: return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'critical': return <AlertTriangle className="h-4 w-4" />;
      case 'warning': return <AlertTriangle className="h-4 w-4" />;
      case 'healthy': return <TrendingUp className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  if (loading && !budgetSummary) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            GCP Budget Dashboard
          </CardTitle>
          <CardDescription>
            Loading budget information...
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-8">
            <RefreshCw className="h-6 w-6 animate-spin" />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            GCP Budget Dashboard
          </CardTitle>
          <CardDescription>
            Error loading budget information
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={fetchBudgetData} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!budgetSummary) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5" />
            GCP Budget Dashboard
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

  const { budget_info, alerts, resource_usage, status } = budgetSummary;

  return (
    <div className={className}>
      <Tabs defaultValue="overview" className="space-y-6">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="alerts">Alerts</TabsTrigger>
            <TabsTrigger value="resources">Resources</TabsTrigger>
            <TabsTrigger value="projections">Projections</TabsTrigger>
          </TabsList>
          
          <div className="flex items-center gap-2">
            {lastRefresh && (
              <span className="text-sm text-gray-500">
                Last updated: {lastRefresh.toLocaleTimeString()}
              </span>
            )}
            <Button 
              onClick={fetchBudgetData} 
              variant="outline" 
              size="sm"
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Project Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5" />
                Project Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <div className="text-sm text-gray-500">Project Name</div>
                  <div className="font-medium">{budget_info.project_name}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Project ID</div>
                  <div className="font-mono text-sm">{budget_info.project_id}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-500">Status</div>
                  <Badge variant={getStatusColor(status)} className="flex items-center gap-1 w-fit">
                    {getStatusIcon(status)}
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Budget Overview */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Budget Overview
              </CardTitle>
              <CardDescription>
                Current month spending and utilization
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Usage Progress */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Monthly Usage</span>
                  <span className="font-medium">
                    ${budget_info.current_month_cost.toFixed(2)} / ${budget_info.monthly_budget_limit}
                  </span>
                </div>
                <Progress 
                  value={budget_info.budget_utilization_percent} 
                  className={`h-3 ${
                    budget_info.is_over_budget ? 'bg-red-500' : 
                    budget_info.is_approaching_limit ? 'bg-yellow-500' : 
                    'bg-green-500'
                  }`}
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>0%</span>
                  <span>{budget_info.budget_utilization_percent.toFixed(1)}%</span>
                  <span>100%</span>
                </div>
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    ${(budget_info.monthly_budget_limit - budget_info.current_month_cost).toFixed(2)}
                  </div>
                  <div className="text-sm text-gray-600">Remaining</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-blue-600">
                    ${budget_info.projected_monthly_cost.toFixed(2)}
                  </div>
                  <div className="text-sm text-gray-600">Projected</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {budget_info.days_remaining_in_month}
                  </div>
                  <div className="text-sm text-gray-600">Days Left</div>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-orange-600">
                    {budget_info.budget_utilization_percent.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-600">Utilization</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Alerts Tab */}
        <TabsContent value="alerts" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Cost Alerts
              </CardTitle>
              <CardDescription>
                Current budget alerts and warnings
              </CardDescription>
            </CardHeader>
            <CardContent>
              {alerts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <TrendingUp className="h-12 w-12 mx-auto mb-4 text-green-500" />
                  <p>No active alerts</p>
                  <p className="text-sm">Your budget usage is within normal limits</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {alerts.map((alert, index) => (
                    <div 
                      key={index}
                      className={`p-4 rounded-lg border ${
                        alert.severity === 'critical' ? 'border-red-200 bg-red-50' :
                        alert.severity === 'high' ? 'border-orange-200 bg-orange-50' :
                        alert.severity === 'medium' ? 'border-yellow-200 bg-yellow-50' :
                        'border-blue-200 bg-blue-50'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <AlertTriangle className={`h-5 w-5 mt-0.5 ${
                          alert.severity === 'critical' ? 'text-red-500' :
                          alert.severity === 'high' ? 'text-orange-500' :
                          alert.severity === 'medium' ? 'text-yellow-500' :
                          'text-blue-500'
                        }`} />
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant={getStatusColor(alert.severity)}>
                              {alert.alert_type.replace('_', ' ').toUpperCase()}
                            </Badge>
                            <span className="text-sm text-gray-500">
                              {new Date(alert.timestamp).toLocaleString()}
                            </span>
                          </div>
                          <p className="text-sm font-medium mb-1">{alert.message}</p>
                          <div className="text-xs text-gray-600">
                            Current: ${alert.current_cost.toFixed(2)} | Threshold: ${alert.threshold.toFixed(2)}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Resources Tab */}
        <TabsContent value="resources" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="h-5 w-5" />
                Resource Usage
              </CardTitle>
              <CardDescription>
                Current resource utilization across GCP services
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Server className="h-5 w-5 text-blue-500" />
                      <div>
                        <div className="font-medium">Compute Instances</div>
                        <div className="text-sm text-gray-500">Active instances</div>
                      </div>
                    </div>
                    <div className="text-2xl font-bold">{resource_usage.compute_instances}</div>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Database className="h-5 w-5 text-green-500" />
                      <div>
                        <div className="font-medium">API Requests</div>
                        <div className="text-sm text-gray-500">Total requests</div>
                      </div>
                    </div>
                    <div className="text-2xl font-bold">{resource_usage.api_requests.toLocaleString()}</div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <HardDrive className="h-5 w-5 text-purple-500" />
                      <div>
                        <div className="font-medium">Storage</div>
                        <div className="text-sm text-gray-500">Data stored</div>
                      </div>
                    </div>
                    <div className="text-2xl font-bold">{resource_usage.storage_gb.toFixed(1)} GB</div>
                  </div>
                  
                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Brain className="h-5 w-5 text-orange-500" />
                      <div>
                        <div className="font-medium">Data Processed</div>
                        <div className="text-sm text-gray-500">ML processing</div>
                      </div>
                    </div>
                    <div className="text-2xl font-bold">{resource_usage.data_processed_gb.toFixed(1)} GB</div>
                  </div>
                </div>
              </div>
              
              <div className="mt-4 text-xs text-gray-500 text-center">
                Last updated: {new Date(resource_usage.last_updated).toLocaleString()}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Projections Tab */}
        <TabsContent value="projections" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Cost Projections
              </CardTitle>
              <CardDescription>
                Monthly cost projections and trends
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="text-sm text-blue-600 font-medium mb-1">Current Month Projection</div>
                    <div className="text-2xl font-bold text-blue-700">
                      ${budget_info.projected_monthly_cost.toFixed(2)}
                    </div>
                    <div className="text-sm text-blue-600">
                      Based on {budget_info.days_remaining_in_month} days remaining
                    </div>
                  </div>
                  
                  <div className="p-4 bg-green-50 rounded-lg">
                    <div className="text-sm text-green-600 font-medium mb-1">Budget Status</div>
                    <div className="text-2xl font-bold text-green-700">
                      {budget_info.projected_monthly_cost <= budget_info.monthly_budget_limit ? 'On Track' : 'Over Budget'}
                    </div>
                    <div className="text-sm text-green-600">
                      {budget_info.projected_monthly_cost <= budget_info.monthly_budget_limit 
                        ? 'Projected to stay within budget' 
                        : 'May exceed monthly budget'
                      }
                    </div>
                  </div>
                </div>
                
                <div className="p-4 bg-gray-50 rounded-lg">
                  <div className="text-sm font-medium mb-2">Cost Trend Analysis</div>
                  <div className="text-sm text-gray-600">
                    {budget_info.budget_utilization_percent > 50 ? (
                      <p>⚠️ High spending rate detected. Consider optimizing resource usage to stay within budget.</p>
                    ) : (
                      <p>✅ Spending rate is healthy. You&apos;re on track to stay within your monthly budget.</p>
                    )}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
