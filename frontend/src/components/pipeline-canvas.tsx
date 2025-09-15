"use client";

import { useState, useCallback, useMemo, useEffect } from "react";
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
  NodeTypes,
} from "reactflow";
import "reactflow/dist/style.css";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Cloud, 
  Database, 
  Brain, 
  Server, 
  Workflow,
  Monitor,
  CheckCircle,
  Clock,
  AlertCircle,
  Save,
  Check
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
        {data.cost && (
          <div className="mt-1 text-xs text-green-600 font-semibold">
            <strong>Cost:</strong> {data.cost}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Custom Edge Components
function DataFlowEdge(props: any) {
  return (
    <div className="text-xs text-blue-600 font-medium">
      {props.data?.label || 'Data Flow'}
    </div>
  );
}

function ControlFlowEdge(props: any) {
  return (
    <div className="text-xs text-gray-600 font-medium">
      {props.data?.label || 'Control Flow'}
    </div>
  );
}

function MLFlowEdge(props: any) {
  return (
    <div className="text-xs text-purple-600 font-medium">
      {props.data?.label || 'ML Flow'}
    </div>
  );
}

// Custom Group Component
function LayerGroup({ data }: { data: any }) {
  const getGroupStyle = (layer: string) => {
    switch (layer) {
      case 'data':
        return 'bg-blue-50 border-blue-200 text-blue-800';
      case 'processing':
        return 'bg-green-50 border-green-200 text-green-800';
      case 'ml':
        return 'bg-purple-50 border-purple-200 text-purple-800';
      case 'application':
        return 'bg-orange-50 border-orange-200 text-orange-800';
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  return (
    <div className={`w-full h-full border-2 rounded-lg p-4 ${getGroupStyle(data.layer)}`}>
      <div className="text-lg font-bold text-center mb-2">{data.label}</div>
      <div className="text-sm text-center opacity-75">{data.description}</div>
    </div>
  );
}

// Node types
const nodeTypes = {
  pipelineNode: PipelineNode,
  layerGroup: LayerGroup,
};

// Edge types
const edgeTypes = {
  dataFlow: DataFlowEdge,
  controlFlow: ControlFlowEdge,
  mlFlow: MLFlowEdge,
};

// Initial nodes for Complete GCP Pipeline
const initialNodes: Node[] = [
  // LAYER GROUPS
  {
    id: 'group-data',
    type: 'layerGroup',
    position: { x: 50, y: 50 },
    style: { width: 600, height: 120 },
    data: { 
      label: 'DATA LAYER',
      description: 'Data collection and storage',
      layer: 'data'
    },
  },
  {
    id: 'group-processing',
    type: 'layerGroup',
    position: { x: 50, y: 200 },
    style: { width: 600, height: 120 },
    data: { 
      label: 'PROCESSING LAYER',
      description: 'Data transformation and orchestration',
      layer: 'processing'
    },
  },
  {
    id: 'group-ml',
    type: 'layerGroup',
    position: { x: 50, y: 350 },
    style: { width: 600, height: 120 },
    data: { 
      label: 'MACHINE LEARNING LAYER',
      description: 'Machine learning and model management',
      layer: 'ml'
    },
  },
  {
    id: 'group-application',
    type: 'layerGroup',
    position: { x: 50, y: 500 },
    style: { width: 600, height: 120 },
    data: { 
      label: 'APPLICATION LAYER',
      description: 'Application serving and user data',
      layer: 'application'
    },
  },
  
  // DATA LAYER SERVICES
  {
    id: 'gcp-1',
    type: 'pipelineNode',
    position: { x: 100, y: 80 },
    data: {
      type: 'data-collection',
      title: 'Cloud Functions',
      description: 'IGDB API data collection',
      status: 'implemented',
      gcpService: 'Cloud Functions',
      localEquivalent: 'IGDBDataCollector + collect_data.py',
      layer: 'data',
      cost: '$0.10/month'
    },
  },
  {
    id: 'gcp-2',
    type: 'pipelineNode',
    position: { x: 300, y: 80 },
    data: {
      type: 'storage',
      title: 'Cloud Storage',
      description: 'Raw data storage',
      status: 'implemented',
      gcpService: 'Cloud Storage',
      localEquivalent: 'data/raw/',
      layer: 'data',
      cost: '$0.50/month'
    },
  },
  {
    id: 'gcp-3',
    type: 'pipelineNode',
    position: { x: 500, y: 80 },
    data: {
      type: 'storage',
      title: 'BigQuery',
      description: 'Data warehouse',
      status: 'implemented',
      gcpService: 'BigQuery',
      localEquivalent: 'BigQuery dataset',
      layer: 'data',
      cost: '$5.00/month'
    },
  },
  
  // PROCESSING LAYER
  {
    id: 'gcp-4',
    type: 'pipelineNode',
    position: { x: 100, y: 230 },
    data: {
      type: 'orchestration',
      title: 'Cloud Composer',
      description: 'Managed Airflow orchestration',
      status: 'pending',
      gcpService: 'Cloud Composer',
      localEquivalent: 'Apache Airflow 3.0',
      layer: 'processing',
      cost: '$300/month'
    },
  },
  {
    id: 'gcp-5',
    type: 'pipelineNode',
    position: { x: 300, y: 230 },
    data: {
      type: 'processing',
      title: 'dbt Cloud',
      description: 'Data transformation',
      status: 'implemented',
      gcpService: 'dbt Cloud',
      localEquivalent: 'dbt_igdb_project',
      layer: 'processing',
      cost: '$50/month'
    },
  },
  
  // ML LAYER
  {
    id: 'gcp-6',
    type: 'pipelineNode',
    position: { x: 100, y: 380 },
    data: {
      type: 'ml',
      title: 'Vertex AI AutoML',
      description: 'Automated ML training',
      status: 'in-progress',
      gcpService: 'Vertex AI AutoML',
      localEquivalent: 'automl_setup.py',
      layer: 'ml',
      cost: '$20/training'
    },
  },
  {
    id: 'gcp-7',
    type: 'pipelineNode',
    position: { x: 300, y: 380 },
    data: {
      type: 'ml',
      title: 'Model Registry',
      description: 'ML model versioning',
      status: 'pending',
      gcpService: 'Vertex AI Model Registry',
      localEquivalent: 'Model persistence',
      layer: 'ml',
      cost: '$10/month'
    },
  },
  
  // APPLICATION LAYER
  {
    id: 'gcp-8',
    type: 'pipelineNode',
    position: { x: 100, y: 530 },
    data: {
      type: 'deployment',
      title: 'Cloud Run',
      description: 'Containerized applications',
      status: 'implemented',
      gcpService: 'Cloud Run',
      localEquivalent: 'FastAPI + Next.js',
      layer: 'application',
      cost: '$15/month'
    },
  },
  {
    id: 'gcp-9',
    type: 'pipelineNode',
    position: { x: 300, y: 530 },
    data: {
      type: 'storage',
      title: 'Cloud SQL',
      description: 'Managed PostgreSQL',
      status: 'pending',
      gcpService: 'Cloud SQL',
      localEquivalent: 'User data storage',
      layer: 'application',
      cost: '$25/month'
    },
  },
];

// Initial edges for GCP Pipeline with custom types
const initialEdges: Edge[] = [
  // Data Layer Flow - Raw data movement
  { 
    id: 'e1-2', 
    source: 'gcp-1', 
    target: 'gcp-2', 
    type: 'dataFlow',
    animated: true,
    style: { stroke: '#3b82f6', strokeWidth: 3 },
    data: { label: 'Raw Data' }
  },
  { 
    id: 'e2-3', 
    source: 'gcp-2', 
    target: 'gcp-3', 
    type: 'dataFlow',
    animated: true,
    style: { stroke: '#3b82f6', strokeWidth: 3 },
    data: { label: 'Structured Data' }
  },
  
  // Processing Layer Flow - Control and data processing
  { 
    id: 'e3-4', 
    source: 'gcp-3', 
    target: 'gcp-4', 
    type: 'controlFlow',
    animated: false,
    style: { stroke: '#6b7280', strokeWidth: 2, strokeDasharray: '5,5' },
    data: { label: 'Trigger' }
  },
  { 
    id: 'e4-5', 
    source: 'gcp-4', 
    target: 'gcp-5', 
    type: 'dataFlow',
    animated: true,
    style: { stroke: '#3b82f6', strokeWidth: 3 },
    data: { label: 'Processed Data' }
  },
  
  // ML Layer Flow - ML-specific data flow
  { 
    id: 'e5-6', 
    source: 'gcp-5', 
    target: 'gcp-6', 
    type: 'mlFlow',
    animated: true,
    style: { stroke: '#a855f7', strokeWidth: 3 },
    data: { label: 'Training Data' }
  },
  { 
    id: 'e6-7', 
    source: 'gcp-6', 
    target: 'gcp-7', 
    type: 'mlFlow',
    animated: true,
    style: { stroke: '#a855f7', strokeWidth: 3 },
    data: { label: 'Trained Model' }
  },
  
  // Application Layer Flow - Serving and user data
  { 
    id: 'e7-8', 
    source: 'gcp-7', 
    target: 'gcp-8', 
    type: 'dataFlow',
    animated: true,
    style: { stroke: '#3b82f6', strokeWidth: 3 },
    data: { label: 'Model API' }
  },
  { 
    id: 'e8-9', 
    source: 'gcp-8', 
    target: 'gcp-9', 
    type: 'dataFlow',
    animated: true,
    style: { stroke: '#3b82f6', strokeWidth: 3 },
    data: { label: 'User Data' }
  },
];

// Local pipeline nodes (original)
const localNodes: Node[] = [
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

// Local pipeline edges
const localEdges: Edge[] = [
  { id: 'e1-2', source: 'local-1', target: 'local-2', animated: true },
  { id: 'e2-3', source: 'local-2', target: 'local-3', animated: true },
  { id: 'e3-4', source: 'local-3', target: 'local-4', animated: true },
  { id: 'e4-5', source: 'local-4', target: 'local-5', animated: true },
  { id: 'e5-6', source: 'local-5', target: 'local-6', animated: true },
];

export function PipelineCanvas() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [savedLayout, setSavedLayout] = useState(false);
  const [showGCP, setShowGCP] = useState(true);

  // Toggle between GCP and Local pipeline
  const togglePipeline = useCallback(() => {
    const newShowGCP = !showGCP;
    
    // Check for saved layout for the target pipeline type
    const storageKey = newShowGCP ? 'pipeline-layout-gcp' : 'pipeline-layout-local';
    const savedLayout = localStorage.getItem(storageKey);
    if (savedLayout) {
      try {
        const layoutData = JSON.parse(savedLayout);
        setNodes(layoutData.nodes);
        setEdges(layoutData.edges);
        setShowGCP(newShowGCP);
        return;
      } catch (error) {
        console.error('Failed to load saved layout:', error);
      }
    }
    
    // Fallback to default nodes if no saved layout
    if (newShowGCP) {
      setNodes(initialNodes);
      setEdges(initialEdges);
    } else {
      setNodes(localNodes);
      setEdges(localEdges);
    }
    setShowGCP(newShowGCP);
  }, [showGCP, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const saveLayout = useCallback(() => {
    // Save current nodes and edges to localStorage
    const layoutData = {
      nodes: nodes,
      edges: edges,
      pipelineType: showGCP ? 'gcp' : 'local',
      timestamp: new Date().toISOString()
    };
    
    // Store in localStorage with separate keys for each pipeline type
    const storageKey = showGCP ? 'pipeline-layout-gcp' : 'pipeline-layout-local';
    localStorage.setItem(storageKey, JSON.stringify(layoutData));
    
    // Show success feedback
    setSavedLayout(true);
    setTimeout(() => setSavedLayout(false), 2000);
  }, [nodes, edges, showGCP]);

  const resetLayout = useCallback(() => {
    // Reset to default layout for current pipeline type
    if (showGCP) {
      setNodes(initialNodes);
      setEdges(initialEdges);
    } else {
      setNodes(localNodes);
      setEdges(localEdges);
    }
    
    // Remove saved layout from localStorage for current pipeline type
    const storageKey = showGCP ? 'pipeline-layout-gcp' : 'pipeline-layout-local';
    localStorage.removeItem(storageKey);
  }, [showGCP, setNodes, setEdges]);

  // Load saved layout on component mount
  useEffect(() => {
    const storageKey = showGCP ? 'pipeline-layout-gcp' : 'pipeline-layout-local';
    const savedLayout = localStorage.getItem(storageKey);
    if (savedLayout) {
      try {
        const layoutData = JSON.parse(savedLayout);
        setNodes(layoutData.nodes);
        setEdges(layoutData.edges);
      } catch (error) {
        console.error('Failed to load saved layout:', error);
      }
    }
  }, [setNodes, setEdges, showGCP]);


  return (
    <div className="w-full h-[calc(100vh-4rem)]">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} />
        <Controls />
        <MiniMap />
        
        <Panel position="top-left">
          <div className="bg-white rounded-lg shadow-lg border p-4">
            <h3 className="font-semibold text-sm mb-3">Data Flow Legend</h3>
            <div className="space-y-2 text-xs">
              <div className="flex items-center gap-2">
                <div className="w-4 h-1 bg-blue-500 rounded"></div>
                <span className="text-blue-600 font-medium">Data Flow</span>
                <span className="text-gray-500">- Raw & processed data</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-1 bg-gray-500 border-dashed border border-gray-500 rounded"></div>
                <span className="text-gray-600 font-medium">Control Flow</span>
                <span className="text-gray-500">- Triggers & orchestration</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-1 bg-purple-500 rounded"></div>
                <span className="text-purple-600 font-medium">ML Flow</span>
                <span className="text-gray-500">- Training & models</span>
              </div>
            </div>
          </div>
        </Panel>

        <Panel position="top-right">
          <div className="space-y-3">
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
            
            <div className="bg-white rounded-lg shadow-lg border p-4">
              <h3 className="font-semibold text-sm mb-2">Layout</h3>
              <div className="space-y-2">
                <Button
                  onClick={saveLayout}
                  variant={savedLayout ? "default" : "outline"}
                  size="sm"
                  className="w-full"
                >
                  {savedLayout ? (
                    <>
                      <Check className="h-4 w-4 mr-1" />
                      Saved!
                    </>
                  ) : (
                    <>
                      <Save className="h-4 w-4 mr-1" />
                      Save Layout
                    </>
                  )}
                </Button>
                <Button
                  onClick={togglePipeline}
                  variant="outline"
                  size="sm"
                  className="w-full"
                >
                  {showGCP ? 'Show Local' : 'Show GCP'}
                </Button>
                <Button
                  onClick={resetLayout}
                  variant="outline"
                  size="sm"
                  className="w-full"
                >
                  Reset Layout
                </Button>
              </div>
            </div>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}
