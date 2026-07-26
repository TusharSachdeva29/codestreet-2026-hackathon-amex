"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
  Handle,
  Position,
  Panel,
} from "reactflow";
import "reactflow/dist/style.css";
import { useSearchParams, useRouter } from "next/navigation";

// ─── Node Type Color Palette ────────────────────────────────────────────────
const NODE_COLORS: Record<string, { bg: string; border: string; icon: string }> = {
  customer_id:        { bg: "#1e3a5f", border: "#3b82f6", icon: "👤" },
  email:              { bg: "#1a3a2a", border: "#10b981", icon: "✉️" },
  phone_number:       { bg: "#2a2a1a", border: "#f59e0b", icon: "📞" },
  card_last4:         { bg: "#3a1a1a", border: "#ef4444", icon: "💳" },
  device_id:          { bg: "#2a1a3a", border: "#8b5cf6", icon: "📱" },
  cookie_id:          { bg: "#1a2a3a", border: "#06b6d4", icon: "🍪" },
  session_id:         { bg: "#2a3a1a", border: "#84cc16", icon: "🔑" },
  browser_fingerprint:{ bg: "#3a2a1a", border: "#f97316", icon: "🖥️" },
  ip_address:         { bg: "#1a1a3a", border: "#a78bfa", icon: "🌐" },
  unknown:            { bg: "#1e293b", border: "#64748b", icon: "❓" },
};

const CONFIDENCE_COLOR = (c: number) =>
  c >= 0.95 ? "#10b981" : c >= 0.75 ? "#f59e0b" : "#ef4444";

const RELATIONSHIP_LABELS: Record<string, string> = {
  VERIFIED_WITH: "Verified With",
  IDENTIFIED_AS: "Identified As",
  USED_CARD:     "Used Card",
  USED_DEVICE:   "Used Device",
  USED_COOKIE:   "Used Cookie",
  USED_SESSION:  "Used Session",
  CONNECTED_TO:  "Connected To",
  SIMILAR_TO:    "Similar To",
};

// ─── Custom Node Component ───────────────────────────────────────────────────
function IdentityNodeComponent({ data }: { data: any }) {
  const colors = NODE_COLORS[data.id_type] || NODE_COLORS.unknown;

  return (
    <div
      style={{
        background: colors.bg,
        border: `2px solid ${colors.border}`,
        borderRadius: "10px",
        padding: "10px 14px",
        minWidth: "130px",
        maxWidth: "180px",
        boxShadow: `0 0 12px ${colors.border}44`,
        position: "relative",
        cursor: "pointer",
        transition: "box-shadow 0.2s",
      }}
    >
      <Handle type="target" position={Position.Top} style={{ background: colors.border }} />
      <div style={{ display: "flex", alignItems: "center", gap: "6px", marginBottom: "4px" }}>
        <span style={{ fontSize: "16px" }}>{colors.icon}</span>
        <span style={{ fontSize: "10px", color: colors.border, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.05em" }}>
          {data.id_type?.replace(/_/g, " ")}
        </span>
        {data.is_trusted && (
          <span style={{ marginLeft: "auto", fontSize: "10px", background: "#10b981", color: "#fff", borderRadius: "4px", padding: "1px 5px" }}>
            ✓ Trusted
          </span>
        )}
      </div>
      <div style={{ fontSize: "12px", color: "#e2e8f0", fontWeight: 600, wordBreak: "break-all", marginBottom: "4px" }}>
        {data.masked_value || (data.id_value?.length > 14 ? data.id_value.slice(0, 12) + "…" : data.id_value)}
      </div>
      <div style={{ display: "flex", gap: "8px", fontSize: "10px", color: "#94a3b8" }}>
        <span>Events: {data.event_count || 1}</span>
        <span>Links: {data.connection_count || 0}</span>
      </div>
      <Handle type="source" position={Position.Bottom} style={{ background: colors.border }} />
    </div>
  );
}

// ─── Custom Edge Component ───────────────────────────────────────────────────
function IdentityEdgeComponent({
  id, sourceX, sourceY, targetX, targetY, data, markerEnd, style,
}: any) {
  const midX = (sourceX + targetX) / 2;
  const midY = (sourceY + targetY) / 2;
  const conf = data?.confidence ?? 0;
  const color = CONFIDENCE_COLOR(conf);
  const strokeWidth = conf >= 0.95 ? 3 : conf >= 0.75 ? 2 : 1.5;

  const path = `M ${sourceX} ${sourceY} Q ${midX} ${midY - 30} ${targetX} ${targetY}`;

  return (
    <g>
      <path d={path} stroke={color} strokeWidth={strokeWidth} fill="none" markerEnd={markerEnd} opacity={0.8} />
      <text>
        <textPath href={`#${id}`} startOffset="50%" textAnchor="middle">
          <tspan dy="-6" fontSize="9" fill={color} fontWeight="600">
            {(conf * 100).toFixed(0)}%
          </tspan>
        </textPath>
      </text>
      <path id={id} d={path} fill="none" stroke="transparent" strokeWidth="12" />
    </g>
  );
}

const nodeTypes = { identityNode: IdentityNodeComponent };
const edgeTypes = { identityEdge: IdentityEdgeComponent };

// ─── Layout helper: cluster-aware positioning ────────────────────────────────
function computeLayout(rawNodes: any[]): any[] {
  const clusterMap: Record<string, any[]> = {};
  rawNodes.forEach((n) => {
    const cid = n.data.customer_id || "unknown";
    if (!clusterMap[cid]) clusterMap[cid] = [];
    clusterMap[cid].push(n);
  });

  const clusterIds = Object.keys(clusterMap);
  const cols = Math.max(Math.ceil(Math.sqrt(clusterIds.length)), 1);
  const CLUSTER_W = 600;
  const CLUSTER_H = 520;
  const INNER_R  = 130;
  const result: any[] = [];

  clusterIds.forEach((clusterId, ci) => {
    const row = Math.floor(ci / cols);
    const col = ci % cols;
    const cx  = col * CLUSTER_W + 300;
    const cy  = row * CLUSTER_H + 280;

    const members = clusterMap[clusterId];
    members.forEach((n, i) => {
      const angle = (i / Math.max(members.length, 1)) * 2 * Math.PI - Math.PI / 2;
      const r = members.length === 1 ? 0 : INNER_R;
      result.push({
        ...n,
        position: {
          x: cx + Math.cos(angle) * r,
          y: cy + Math.sin(angle) * r,
        },
      });
    });
  });

  return result;
}

// ─── Main Page ───────────────────────────────────────────────────────────────
export default function IdentityGraphPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const customerId = searchParams.get("customer_id") || "";

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [stats, setStats]         = useState<any>({});
  const [clusters, setClusters]   = useState<any[]>([]);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [selectedEdge, setSelectedEdge] = useState<any>(null);
  const [searchId, setSearchId]   = useState(customerId);
  const [loading, setLoading]     = useState(true);
  const [filterType, setFilterType] = useState<string>("all");
  const [filterConf, setFilterConf] = useState<number>(0);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const intervalRef = useRef<any>(null);

  const fetchGraph = useCallback(
    async (cId: string) => {
      setLoading(true);
      try {
        const url = cId
          ? `http://localhost:8000/api/v1/graph?customer_id=${encodeURIComponent(cId)}`
          : "http://localhost:8000/api/v1/graph";
        const res  = await fetch(url);
        const data = await res.json();

        // Apply node type filter
        let filteredNodes = data.nodes || [];
        if (filterType !== "all") {
          filteredNodes = filteredNodes.filter((n: any) => n.data.id_type === filterType);
        }

        // Add masked_value to each node
        filteredNodes = filteredNodes.map((n: any) => {
          const v = n.data.id_value || "";
          const masked = n.data.id_type in { email: 1, phone_number: 1, card_last4: 1 }
            ? (v.length > 5 ? v.slice(0, 3) + "***" + v.slice(-2) : "***")
            : v.length > 14 ? v.slice(0, 12) + "…" : v;
          return { ...n, data: { ...n.data, masked_value: masked } };
        });

        const filteredNodeIds = new Set(filteredNodes.map((n: any) => n.id));

        // Apply confidence filter on edges
        let filteredEdges = (data.edges || []).filter(
          (e: any) =>
            e.data.confidence >= filterConf &&
            filteredNodeIds.has(e.source) &&
            filteredNodeIds.has(e.target)
        );

        // Apply styling to edges
        filteredEdges = filteredEdges.map((e: any) => ({
          ...e,
          markerEnd: { type: MarkerType.ArrowClosed, color: CONFIDENCE_COLOR(e.data.confidence) },
          style: {
            stroke: CONFIDENCE_COLOR(e.data.confidence),
            strokeWidth: e.data.confidence >= 0.95 ? 3 : e.data.confidence >= 0.75 ? 2 : 1.5,
          },
        }));

        const laidOut = computeLayout(filteredNodes);
        setNodes(laidOut);
        setEdges(filteredEdges);
        setStats(data.stats || {});
        setClusters(data.clusters || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    },
    [setNodes, setEdges, filterType, filterConf]
  );

  useEffect(() => {
    fetchGraph(customerId);
  }, [customerId, fetchGraph]);

  // Auto-refresh
  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(() => fetchGraph(customerId), 5000);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [autoRefresh, customerId, fetchGraph]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchId) router.push(`/dashboard/graph?customer_id=${searchId}`);
    else router.push("/dashboard/graph");
  };

  const onNodeClick = (_: any, node: any) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  };
  const onEdgeClick = (_: any, edge: any) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
  };
  const onPaneClick = () => {
    setSelectedNode(null);
    setSelectedEdge(null);
  };

  const allTypes = Array.from(new Set(nodes.map((n: any) => n.data?.id_type).filter(Boolean)));

  return (
    <div className="dashboard-page graph-page" style={{ height: "100%", display: "flex", flexDirection: "column", gap: "1rem" }}>
      {/* Header */}
      <header className="page-header" style={{ marginBottom: 0 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <h1 style={{ marginBottom: "0.25rem" }}>Identity Graph</h1>
            <p style={{ color: "#94a3b8", margin: 0 }}>
              Live view of customer identity clusters, connections, and confidence scores
            </p>
          </div>
          {/* Stats Bar */}
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            {[
              { label: "Customers", value: stats.total_customers ?? stats.connected_components ?? "—" },
              { label: "Nodes",     value: stats.total_nodes ?? "—" },
              { label: "Edges",     value: stats.total_edges ?? "—" },
              { label: "Avg IDs",   value: stats.avg_identifiers_per_customer ?? stats.avg_identifiers ?? "—" },
              { label: "Largest",   value: stats.largest_cluster ?? "—" },
            ].map((s) => (
              <div key={s.label} style={{ background: "#0f172a", border: "1px solid #1e293b", borderRadius: "8px", padding: "0.5rem 1rem", textAlign: "center", minWidth: "80px" }}>
                <div style={{ fontSize: "1.3rem", fontWeight: 700, color: "#3b82f6" }}>{s.value}</div>
                <div style={{ fontSize: "0.75rem", color: "#64748b" }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </header>

      {/* Controls Row */}
      <div style={{ display: "flex", gap: "1rem", alignItems: "center", flexWrap: "wrap" }}>
        <form onSubmit={handleSearch} style={{ display: "flex", gap: "0.5rem", flex: 1, minWidth: "280px" }}>
          <input
            type="text"
            placeholder="Search by Customer ID…"
            value={searchId}
            onChange={(e) => setSearchId(e.target.value)}
            style={{ flex: 1, padding: "0.6rem 1rem", borderRadius: "8px", border: "1px solid #334155", background: "#0f172a", color: "#fff", fontSize: "0.9rem" }}
          />
          <button type="submit" style={{ padding: "0.6rem 1.2rem", borderRadius: "8px", background: "#3b82f6", color: "#fff", border: "none", cursor: "pointer", fontWeight: 600 }}>
            Filter
          </button>
          {customerId && (
            <button type="button" onClick={() => { setSearchId(""); router.push("/dashboard/graph"); }}
              style={{ padding: "0.6rem 1rem", borderRadius: "8px", background: "#334155", color: "#fff", border: "none", cursor: "pointer" }}>
              Clear
            </button>
          )}
        </form>

        {/* Type Filter */}
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          style={{ padding: "0.6rem 1rem", borderRadius: "8px", border: "1px solid #334155", background: "#0f172a", color: "#fff", fontSize: "0.85rem" }}
        >
          <option value="all">All Types</option>
          {allTypes.map((t) => (
            <option key={t} value={t}>{t?.replace(/_/g, " ")}</option>
          ))}
        </select>

        {/* Confidence Filter */}
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <label style={{ fontSize: "0.85rem", color: "#94a3b8", whiteSpace: "nowrap" }}>
            Min Conf: {(filterConf * 100).toFixed(0)}%
          </label>
          <input type="range" min={0} max={1} step={0.05} value={filterConf}
            onChange={(e) => setFilterConf(parseFloat(e.target.value))}
            style={{ width: "100px" }}
          />
        </div>

        {/* Auto-refresh */}
        <button
          onClick={() => setAutoRefresh(!autoRefresh)}
          style={{ padding: "0.6rem 1.2rem", borderRadius: "8px", background: autoRefresh ? "#10b981" : "#334155", color: "#fff", border: "none", cursor: "pointer", fontWeight: 600, fontSize: "0.85rem" }}
        >
          {autoRefresh ? "⟳ Live" : "⟳ Auto"}
        </button>

        <button
          onClick={() => fetchGraph(customerId)}
          style={{ padding: "0.6rem 1.2rem", borderRadius: "8px", background: "#1e293b", color: "#fff", border: "1px solid #334155", cursor: "pointer" }}
        >
          Refresh
        </button>
      </div>

      {/* Legend */}
      <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
        <span style={{ fontSize: "0.8rem", color: "#64748b" }}>Node Types:</span>
        {Object.entries(NODE_COLORS).slice(0, 8).map(([type, colors]) => (
          <div key={type} style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "0.78rem", color: colors.border }}>
            <div style={{ width: "10px", height: "10px", borderRadius: "2px", background: colors.border, opacity: 0.8 }} />
            {type.replace(/_/g, " ")}
          </div>
        ))}
        <span style={{ marginLeft: "1rem", fontSize: "0.8rem", color: "#64748b" }}>Confidence:</span>
        {[{ label: "High ≥95%", color: "#10b981" }, { label: "Med ≥75%", color: "#f59e0b" }, { label: "Low <75%", color: "#ef4444" }].map((c) => (
          <div key={c.label} style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "0.78rem", color: c.color }}>
            <div style={{ width: "22px", height: "3px", background: c.color, borderRadius: "2px" }} />
            {c.label}
          </div>
        ))}
      </div>

      {/* Main Canvas + Side Panel */}
      <div style={{ display: "flex", flex: 1, gap: "1rem", minHeight: "560px" }}>
        {/* Cluster Sidebar */}
        {clusters.length > 0 && !customerId && (
          <div style={{ width: "200px", background: "#0f172a", borderRadius: "12px", border: "1px solid #1e293b", padding: "1rem", overflowY: "auto", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            <h4 style={{ color: "#94a3b8", fontSize: "0.75rem", textTransform: "uppercase", letterSpacing: "0.08em", margin: "0 0 0.5rem" }}>
              Clusters ({clusters.length})
            </h4>
            {clusters.slice(0, 30).map((c) => (
              <button
                key={c.customer_id}
                onClick={() => router.push(`/dashboard/graph?customer_id=${c.customer_id}`)}
                style={{ background: "#1e293b", border: "1px solid #334155", borderRadius: "8px", padding: "0.5rem 0.75rem", cursor: "pointer", textAlign: "left", color: "#e2e8f0" }}
              >
                <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "2px" }}>
                  {c.customer_id.slice(0, 8)}…
                </div>
                <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
                  <span style={{ fontSize: "0.7rem", color: "#3b82f6" }}>{c.node_count} nodes</span>
                  {c.has_trusted_id && (
                    <span style={{ fontSize: "0.7rem", color: "#10b981" }}>✓ verified</span>
                  )}
                </div>
              </button>
            ))}
          </div>
        )}

        {/* React Flow Canvas */}
        <div style={{ flex: 1, background: "#080f1e", borderRadius: "12px", overflow: "hidden", border: "1px solid #1e293b", position: "relative" }}>
          {loading && (
            <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", color: "#94a3b8", zIndex: 10, textAlign: "center" }}>
              <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>⟳</div>
              <div>Loading Identity Graph…</div>
            </div>
          )}

          {!loading && nodes.length === 0 && (
            <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)", color: "#64748b", textAlign: "center" }}>
              <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>🕸️</div>
              <div style={{ fontSize: "1.1rem" }}>No identity nodes found.</div>
              <div style={{ fontSize: "0.9rem", marginTop: "0.5rem" }}>Fire some events from the simulator to build the graph.</div>
            </div>
          )}

          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            onPaneClick={onPaneClick}
            fitView
            fitViewOptions={{ padding: 0.15 }}
            attributionPosition="bottom-right"
          >
            <MiniMap
              style={{ height: 100, background: "#0f172a", border: "1px solid #1e293b" }}
              nodeColor={(n: any) => NODE_COLORS[n.data?.id_type]?.border ?? "#64748b"}
            />
            <Controls style={{ background: "#1e293b", border: "1px solid #334155" }} />
            <Background color="#1e293b" gap={20} size={1} />
          </ReactFlow>
        </div>

        {/* Node Details Panel */}
        {selectedNode && (
          <div style={{ width: "300px", background: "#0f172a", borderRadius: "12px", border: `1px solid ${NODE_COLORS[selectedNode.data?.id_type]?.border ?? "#334155"}`, padding: "1.5rem", color: "#e2e8f0", overflowY: "auto", display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #1e293b", paddingBottom: "0.75rem" }}>
              <h3 style={{ color: "#fff", margin: 0, fontSize: "1rem" }}>
                {NODE_COLORS[selectedNode.data?.id_type]?.icon} Node Details
              </h3>
              <button onClick={() => setSelectedNode(null)} style={{ background: "none", border: "none", color: "#64748b", cursor: "pointer", fontSize: "1.2rem" }}>✕</button>
            </div>

            {[
              { label: "Type", value: selectedNode.data.id_type?.replace(/_/g, " "), color: NODE_COLORS[selectedNode.data?.id_type]?.border },
              { label: "Value (Masked)", value: selectedNode.data.masked_value },
              { label: "Customer ID", value: selectedNode.data.customer_id?.slice(0, 18) + "…" },
              { label: "Event Count", value: selectedNode.data.event_count },
              { label: "Connections", value: selectedNode.data.connection_count },
              { label: "Trusted ID", value: selectedNode.data.is_trusted ? "✓ Yes" : "No", color: selectedNode.data.is_trusted ? "#10b981" : "#64748b" },
            ].map((row) => (
              <div key={row.label}>
                <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "2px", textTransform: "uppercase", letterSpacing: "0.05em" }}>{row.label}</div>
                <div style={{ fontSize: "0.95rem", fontWeight: 600, color: row.color ?? "#e2e8f0" }}>{row.value ?? "—"}</div>
              </div>
            ))}

            {selectedNode.data.first_seen && (
              <div>
                <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "2px", textTransform: "uppercase", letterSpacing: "0.05em" }}>First Seen</div>
                <div style={{ fontSize: "0.85rem", color: "#94a3b8" }}>{new Date(selectedNode.data.first_seen).toLocaleString()}</div>
              </div>
            )}
            {selectedNode.data.last_seen && (
              <div>
                <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "2px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Last Seen</div>
                <div style={{ fontSize: "0.85rem", color: "#94a3b8" }}>{new Date(selectedNode.data.last_seen).toLocaleString()}</div>
              </div>
            )}

            <button
              onClick={() => router.push(`/dashboard/graph?customer_id=${selectedNode.data.customer_id}`)}
              style={{ padding: "0.6rem", borderRadius: "8px", background: "#1e40af", color: "#fff", border: "none", cursor: "pointer", fontSize: "0.85rem", fontWeight: 600 }}
            >
              View Full Cluster →
            </button>
          </div>
        )}

        {/* Edge Details Panel */}
        {selectedEdge && (
          <div style={{ width: "300px", background: "#0f172a", borderRadius: "12px", border: `1px solid ${CONFIDENCE_COLOR(selectedEdge.data?.confidence ?? 0)}`, padding: "1.5rem", color: "#e2e8f0", overflowY: "auto", display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid #1e293b", paddingBottom: "0.75rem" }}>
              <h3 style={{ color: "#fff", margin: 0, fontSize: "1rem" }}>🔗 Edge Details</h3>
              <button onClick={() => setSelectedEdge(null)} style={{ background: "none", border: "none", color: "#64748b", cursor: "pointer", fontSize: "1.2rem" }}>✕</button>
            </div>

            {/* Confidence Gauge */}
            <div>
              <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "6px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Confidence Score</div>
              <div style={{ fontSize: "2rem", fontWeight: 800, color: CONFIDENCE_COLOR(selectedEdge.data?.confidence ?? 0) }}>
                {((selectedEdge.data?.confidence ?? 0) * 100).toFixed(1)}%
              </div>
              <div style={{ height: "6px", background: "#1e293b", borderRadius: "3px", marginTop: "6px" }}>
                <div style={{ height: "100%", width: `${(selectedEdge.data?.confidence ?? 0) * 100}%`, background: CONFIDENCE_COLOR(selectedEdge.data?.confidence ?? 0), borderRadius: "3px", transition: "width 0.4s" }} />
              </div>
            </div>

            <div>
              <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "2px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Relationship</div>
              <div style={{ fontSize: "0.95rem", fontWeight: 600, color: "#60a5fa" }}>
                {RELATIONSHIP_LABELS[selectedEdge.data?.relationship_type] ?? selectedEdge.data?.relationship_type ?? "Connected To"}
              </div>
            </div>

            <div>
              <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "6px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Evidence / Reasoning</div>
              {selectedEdge.data?.evidence?.length > 0 ? (
                <ul style={{ margin: 0, paddingLeft: "1.2rem", display: "flex", flexDirection: "column", gap: "4px" }}>
                  {selectedEdge.data.evidence.map((ev: string, i: number) => (
                    <li key={i} style={{ fontSize: "0.85rem", color: "#cbd5e1" }}>{ev}</li>
                  ))}
                </ul>
              ) : (
                <div style={{ fontSize: "0.85rem", color: "#475569" }}>No evidence recorded.</div>
              )}
            </div>

            {selectedEdge.data?.created_at && (
              <div>
                <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "2px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Created At</div>
                <div style={{ fontSize: "0.85rem", color: "#94a3b8" }}>{new Date(selectedEdge.data.created_at).toLocaleString()}</div>
              </div>
            )}
            {selectedEdge.data?.last_updated && (
              <div>
                <div style={{ fontSize: "0.75rem", color: "#64748b", marginBottom: "2px", textTransform: "uppercase", letterSpacing: "0.05em" }}>Last Updated</div>
                <div style={{ fontSize: "0.85rem", color: "#94a3b8" }}>{new Date(selectedEdge.data.last_updated).toLocaleString()}</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
