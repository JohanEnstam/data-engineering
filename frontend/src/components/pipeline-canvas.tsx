"use client";

import { useState, useCallback, useMemo } from "react";
import ReactFlow, {
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  BackgroundVariant,
  MiniMap,
  Panel,
} from "reactflow";
import "reactflow/dist/style.css";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Plus, 
  Cloud, 
  Database, 
  Brain, 
  Server, 
  Workflow,
  Monitor,
  CheckCircle,
  Clock,
  AlertCircle
} from "lucide-react";

// Custom Node Component
function PipelineNode({ data }: { data: any }) {
  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'data-collection': return <Cloud className="h-5 w-5" />;
      case 'storage': return <Database className="h-5 w-5" />;
      case 'processing': return <Workflow className="h-5 w-5" />;
      case 'ml': return <Brain className="h-5 w-5" />;
      case 'orchestration': return <Workflow className="h-5 w-5" />;
      case 'deployment': return <Server className="h-5 w-5" />;
      case 'monitoring': return <Monitor className="h-5 w-5" />;
      default: return <Cloud className="h-5 w-5" />;
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'implemented': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'in-progress': return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'pending': return <AlertCircle className="h-4 w-4 text-orange-500" />;
      default: return <AlertCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'implemented': return 'bg-green-100 text-green-800 border-green-200';
      case 'in-progress': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'pending': return 'bg-orange-100 text-orange-800 border-orange-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <Card className="shadow-lg min-w-[200px]">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getNodeIcon(data.type)}
            <CardTitle className="text-sm">{data.title}</CardTitle>
          </div>
          {getStatusIcon(data.status)}
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <p className="text-xs text-gray-600 mb-2">{data.description}</p>
        <Badge className={`text-xs ${getStatusColor(data.status)}`}>
          {data.status.replace('-', ' ').toUpperCase()}
        </Badge>
        {data.gcpService && (
          <div className="mt-2 text-xs text-blue-600">
            <strong>GCP:</strong> {data.gcpService}
          </div>
        )}
        {data.localEquivalent && (
          <div className="mt-1 text-xs text-gray-600">
            <strong>Local:</strong> {data.localEquivalent}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Node types
const nodeTypes = {
  pipelineNode: PipelineNode,
};

// Initial nodes for Local Pipeline
const initialNodes: Node[] = [
  {
    id: 'local-1',
    type: 'pipelineNode',
    position: { x: 100, y: 100 },
    data: {
      type: 'data-collection',
      title: 'Data Collection',
      description: 'IGDB API data collection',
      status: 'implemented',
      gcpService: 'Cloud Functions',
      localEquivalent: 'IGDBDataCollector + collect_data.py'
    },
  },
  {
    id: 'local-2',
    type: 'pipelineNode',
    position: { x: 100, y: 250 },
    data: {
      type: 'storage',
      title: 'Data Storage',
      description: 'Raw data storage and processing',
      status: 'implemented',
      gcpService: 'Cloud Storage + BigQuery',
      localEquivalent: 'data/raw/ + BigQuery'
    },
  },
  {
    id: 'local-3',
    type: 'pipelineNode',
    position: { x: 100, y: 400 },
    data: {
      type: 'processing',
      title: 'Data Processing',
      description: 'ETL and data transformation',
      status: 'implemented',
      gcpService: 'dbt Cloud + BigQuery',
      localEquivalent: 'dbt_igdb_project + ETLPipeline'
    },
  },
  {
    id: 'local-4',
    type: 'pipelineNode',
    position: { x: 100, y: 550 },
    data: {
      type: 'ml',
      title: 'ML Training',
      description: 'Recommendation model training',
      status: 'in-progress',
      gcpService: 'Vertex AI AutoML',
      localEquivalent: 'GameRecommender + automl_setup.py'
    },
  },
  {
    id: 'local-5',
    type: 'pipelineNode',
    position: { x: 100, y: 700 },
    data: {
      type: 'deployment',
      title: 'API & Frontend',
      description: 'Application serving layer',
      status: 'implemented',
      gcpService: 'Cloud Run',
      localEquivalent: 'FastAPI + Next.js + Docker'
    },
  },
  {
    id: 'local-6',
    type: 'pipelineNode',
    position: { x: 100, y: 850 },
    data: {
      type: 'orchestration',
      title: 'Orchestration',
      description: 'Pipeline automation',
      status: 'pending',
      gcpService: 'Cloud Composer',
      localEquivalent: 'Apache Airflow 3.0 + DAGs'
    },
  },
];

// Initial edges
const initialEdges: Edge[] = [
  { id: 'e1-2', source: 'local-1', target: 'local-2', animated: true },
  { id: 'e2-3', source: 'local-2', target: 'local-3', animated: true },
  { id: 'e3-4', source: 'local-3', target: 'local-4', animated: true },
  { id: 'e4-5', source: 'local-4', target: 'local-5', animated: true },
  { id: 'e5-6', source: 'local-5', target: 'local-6', animated: true },
];

export function PipelineCanvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const addNode = useCallback((type: string, title: string, description: string, status: string) => {
    const newNode: Node = {
      id: `node-${Date.now()}`,
      type: 'pipelineNode',
      position: { x: Math.random() * 400 + 500, y: Math.random() * 400 + 200 },
      data: {
        type,
        title,
        description,
        status,
      },
    };
    setNodes((nds) => [...nds, newNode]);
  }, [setNodes]);

  return (
    <div className="w-full h-screen">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
        <Controls />
        <MiniMap />
        
        <Panel position="top-left">
          <div className="bg-white rounded-lg shadow-lg border p-4 space-y-2">
            <h3 className="font-semibold text-sm mb-2">Add Nodes</h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => addNode('data-collection', 'Data Collection', 'New data collection node', 'not-started')}
            >
              <Plus className="h-4 w-4 mr-1" />
              Data Collection
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => addNode('storage', 'Storage', 'New storage node', 'not-started')}
            >
              <Plus className="h-4 w-4 mr-1" />
              Storage
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => addNode('processing', 'Processing', 'New processing node', 'not-started')}
            >
              <Plus className="h-4 w-4 mr-1" />
              Processing
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => addNode('ml', 'ML/AI', 'New ML node', 'not-started')}
            >
              <Plus className="h-4 w-4 mr-1" />
              ML/AI
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => addNode('deployment', 'Deployment', 'New deployment node', 'not-started')}
            >
              <Plus className="h-4 w-4 mr-1" />
              Deployment
            </Button>
          </div>
        </Panel>

        <Panel position="top-right">
          <div className="bg-white rounded-lg shadow-lg border p-4">
            <h3 className="font-semibold text-sm mb-2">Pipeline Status</h3>
            <div className="space-y-1 text-xs">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-3 w-3 text-green-500" />
                <span>Implemented: {nodes.filter(n => n.data.status === 'implemented').length}</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-3 w-3 text-yellow-500" />
                <span>In Progress: {nodes.filter(n => n.data.status === 'in-progress').length}</span>
              </div>
              <div className="flex items-center gap-2">
                <AlertCircle className="h-3 w-3 text-orange-500" />
                <span>Pending: {nodes.filter(n => n.data.status === 'pending').length}</span>
              </div>
            </div>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}
