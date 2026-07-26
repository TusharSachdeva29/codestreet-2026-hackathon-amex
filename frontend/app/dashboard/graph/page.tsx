"use client";

import { useEffect, useState, useCallback, useMemo } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useSearchParams, useRouter } from 'next/navigation';

export default function IdentityGraphPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const customerId = searchParams.get('customer_id') || '';

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [stats, setStats] = useState({ total_nodes: 0, total_edges: 0 });
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [selectedEdge, setSelectedEdge] = useState<any>(null);
  const [searchId, setSearchId] = useState(customerId);
  const [loading, setLoading] = useState(true);

  const fetchGraph = useCallback(async (cId: string) => {
    setLoading(true);
    try {
      const url = cId 
        ? `http://localhost:8000/api/v1/graph?customer_id=${encodeURIComponent(cId)}`
        : 'http://localhost:8000/api/v1/graph';
      
      const res = await fetch(url);
      const data = await res.json();
      
      // Group nodes by customer_id to create distinct clusters visually
      const clusterMap: Record<string, any[]> = {};
      data.nodes.forEach((n: any) => {
        const cId = n.data.customer_id || 'unknown';
        if (!clusterMap[cId]) clusterMap[cId] = [];
        clusterMap[cId].push(n);
      });

      const clusterIds = Object.keys(clusterMap);
      const formattedNodes: any[] = [];
      
      // We will place each cluster in a grid
      const cols = Math.ceil(Math.sqrt(clusterIds.length)) || 1;
      const xSpacing = 500;
      const ySpacing = 500;

      clusterIds.forEach((clusterId, clusterIndex) => {
        const clusterNodes = clusterMap[clusterId];
        // Cluster center
        const row = Math.floor(clusterIndex / cols);
        const col = clusterIndex % cols;
        const cx = col * xSpacing + 400;
        const cy = row * ySpacing + 300;
        
        // Layout nodes in this cluster as a small circle
        const radius = clusterNodes.length > 1 ? 120 : 0;
        
        clusterNodes.forEach((n: any, i: number) => {
          const angle = (i / clusterNodes.length) * 2 * Math.PI;
          formattedNodes.push({
            ...n,
            position: {
              x: cx + Math.cos(angle) * radius,
              y: cy + Math.sin(angle) * radius
            },
            style: {
              background: '#1e293b',
              color: '#fff',
              border: '1px solid #3b82f6',
              borderRadius: '8px',
              padding: '10px',
              fontSize: '12px',
              minWidth: '100px',
              textAlign: 'center'
            }
          });
        });
      });

      const formattedEdges = data.edges.map((e: any) => ({
        ...e,
        markerEnd: { type: MarkerType.ArrowClosed, color: '#94a3b8' },
        style: { stroke: '#94a3b8', strokeWidth: 2 }
      }));

      setNodes(formattedNodes);
      setEdges(formattedEdges);
      setStats(data.stats);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [setNodes, setEdges]);

  useEffect(() => {
    fetchGraph(customerId);
  }, [customerId, fetchGraph]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchId) {
      router.push(`/dashboard/graph?customer_id=${searchId}`);
    } else {
      router.push('/dashboard/graph');
    }
  };

  const onNodeClick = (event: any, node: any) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  };

  const onEdgeClick = (event: any, edge: any) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
  };

  return (
    <div className="dashboard-page graph-page" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <header className="page-header" style={{ marginBottom: '1rem' }}>
        <h1>Identity Graph Visualization</h1>
        <p>Interactive view of customer identifiers and their relationships</p>
      </header>

      <div style={{ display: 'flex', gap: '2rem', marginBottom: '1rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', flex: 1 }}>
          <input 
            type="text" 
            placeholder="Enter Customer ID to highlight their graph..." 
            value={searchId}
            onChange={(e) => setSearchId(e.target.value)}
            style={{ flex: 1, padding: '0.8rem', borderRadius: '8px', border: '1px solid #334155', background: '#0f172a', color: '#fff' }}
          />
          <button type="submit" style={{ padding: '0.8rem 1.5rem', borderRadius: '8px', background: '#3b82f6', color: '#fff', border: 'none', cursor: 'pointer' }}>
            Filter Graph
          </button>
        </form>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <div className="badge">Total Nodes: {stats.total_nodes}</div>
          <div className="badge">Total Edges: {stats.total_edges}</div>
        </div>
      </div>

      <div style={{ display: 'flex', flex: 1, gap: '1rem', minHeight: '600px' }}>
        <div style={{ flex: 1, background: '#0f172a', borderRadius: '12px', overflow: 'hidden', border: '1px solid #1e293b', position: 'relative' }}>
          {loading && <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', color: '#94a3b8', zIndex: 10 }}>Loading Graph...</div>}
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            fitView
            attributionPosition="bottom-right"
          >
            <MiniMap style={{ height: 120, background: '#1e293b' }} nodeColor="#3b82f6" />
            <Controls style={{ background: '#1e293b' }} />
            <Background color="#334155" gap={16} />
          </ReactFlow>
        </div>
        
        {selectedNode && (
          <div style={{ width: '300px', background: '#0f172a', borderRadius: '12px', border: '1px solid #1e293b', padding: '1.5rem', color: '#e2e8f0' }}>
            <h3 style={{ marginBottom: '1.5rem', color: '#fff', borderBottom: '1px solid #1e293b', paddingBottom: '0.5rem' }}>Node Details</h3>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Identifier Type</label>
              <div style={{ fontSize: '1.1rem', marginTop: '0.2rem', textTransform: 'capitalize' }}>{selectedNode.data.type}</div>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Value (Masked)</label>
              <div style={{ fontSize: '1.1rem', marginTop: '0.2rem', wordBreak: 'break-all' }}>
                {selectedNode.data.label.length > 5 ? selectedNode.data.label.substring(0, 3) + '***' + selectedNode.data.label.substring(selectedNode.data.label.length - 2) : selectedNode.data.label}
              </div>
            </div>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Match Confidence</label>
              <div style={{ fontSize: '1.1rem', marginTop: '0.2rem', color: '#10b981' }}>See Edge Labels</div>
            </div>
            
            {selectedNode.data.first_seen && (
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ color: '#94a3b8', fontSize: '0.85rem' }}>First Seen</label>
                <div style={{ fontSize: '0.9rem', marginTop: '0.2rem', color: '#e2e8f0' }}>{new Date(selectedNode.data.first_seen).toLocaleString()}</div>
              </div>
            )}
            
            {selectedNode.data.last_seen && (
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Last Seen</label>
                <div style={{ fontSize: '0.9rem', marginTop: '0.2rem', color: '#e2e8f0' }}>{new Date(selectedNode.data.last_seen).toLocaleString()}</div>
              </div>
            )}
            
            <div style={{ marginTop: '2rem' }}>
              <button onClick={() => setSelectedNode(null)} style={{ padding: '0.5rem 1rem', background: '#334155', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', width: '100%' }}>
                Close Panel
              </button>
            </div>
          </div>
        )}
        
        {selectedEdge && (
          <div style={{ width: '300px', background: '#0f172a', borderRadius: '12px', border: '1px solid #1e293b', padding: '1.5rem', color: '#e2e8f0', overflowY: 'auto' }}>
            <h3 style={{ marginBottom: '1.5rem', color: '#fff', borderBottom: '1px solid #1e293b', paddingBottom: '0.5rem' }}>Edge Details</h3>
            
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Confidence Score</label>
              <div style={{ fontSize: '1.3rem', marginTop: '0.2rem', color: selectedEdge.data.confidence >= 0.95 ? '#10b981' : '#f59e0b', fontWeight: 'bold' }}>
                {selectedEdge.data.confidence.toFixed(2)}
              </div>
            </div>
            
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Evidence / Rules Applied</label>
              <ul style={{ marginTop: '0.5rem', paddingLeft: '1.2rem', fontSize: '0.9rem', color: '#cbd5e1' }}>
                {selectedEdge.data.evidence && selectedEdge.data.evidence.length > 0 ? (
                  selectedEdge.data.evidence.map((ev: string, i: number) => (
                    <li key={i} style={{ marginBottom: '0.3rem' }}>{ev}</li>
                  ))
                ) : (
                  <li>No evidence recorded</li>
                )}
              </ul>
            </div>
            
            {selectedEdge.data.created_at && (
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Created At</label>
                <div style={{ fontSize: '0.9rem', marginTop: '0.2rem', color: '#94a3b8' }}>{new Date(selectedEdge.data.created_at).toLocaleString()}</div>
              </div>
            )}
            
            <div style={{ marginTop: '2rem' }}>
              <button onClick={() => setSelectedEdge(null)} style={{ padding: '0.5rem 1rem', background: '#334155', color: '#fff', border: 'none', borderRadius: '6px', cursor: 'pointer', width: '100%' }}>
                Close Panel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
