import { useCallback, useEffect, useState } from 'react'
import ReactFlow, { Background, Controls, MiniMap, useNodesState, useEdgesState } from 'reactflow'
import 'reactflow/dist/style.css'
import { api } from '../services/api'
import LoadingState from '../components/LoadingState'

const nodeColors = { trader: '#3b82f6', insider: '#ef4444', company: '#10b981', device: '#f59e0b' }

export default function GraphExplorer() {
  const [nodes, setNodes, onNodesChange] = useNodesState([])
  const [edges, setEdges, onEdgesChange] = useEdgesState([])
  const [metrics, setMetrics] = useState(null)

  const layout = useCallback((data) => {
    const n = data.nodes.map((node, i) => ({
      id: node.id,
      data: { label: `${node.label}\n(${node.type})` },
      position: { x: (i % 4) * 200, y: Math.floor(i / 4) * 120 },
      style: {
        background: nodeColors[node.type] || '#64748b',
        color: '#fff',
        fontSize: 11,
        border: '1px solid #334155',
        borderRadius: 8,
        padding: 8,
        width: 140,
      },
    }))
    const e = data.edges.map((edge, i) => ({
      id: `e-${i}`,
      source: edge.source,
      target: edge.target,
      label: edge.type,
      animated: edge.suspicious,
      style: { stroke: edge.suspicious ? '#ef4444' : '#64748b' },
    }))
    setNodes(n)
    setEdges(e)
    setMetrics(data.metrics)
  }, [setNodes, setEdges])

  useEffect(() => {
    api.graph().then(layout).catch(console.error)
  }, [layout])

  if (!nodes.length) return <LoadingState />

  return (
    <div className="p-6 h-screen flex flex-col">
      <h2 className="text-xl font-bold text-white mb-2">Insider Relationship Graph</h2>
      {metrics && (
        <div className="flex gap-4 text-xs text-slate-400 mb-2">
          <span>Cluster score: <b className="text-amber-400">{metrics.cluster_score}</b></span>
          <span>Event coordination: <b className="text-red-400">{metrics.event_coordination_score}</b></span>
          <span>Insider proximity: <b className="text-accent-cyan">{metrics.insider_proximity_score}</b></span>
        </div>
      )}
      <div className="flex-1 card min-h-[500px]">
        <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} fitView>
          <Background color="#334155" gap={16} />
          <Controls />
          <MiniMap nodeColor={(n) => n.style?.background} />
        </ReactFlow>
      </div>
    </div>
  )
}
