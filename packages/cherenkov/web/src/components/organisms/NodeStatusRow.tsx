import { cn } from '@/src/lib/utils';
import { CyberButton } from '../atoms/CyberButton';
import { Database, ShieldAlert, Cpu, Network, Box } from 'lucide-react';
import { ReactNode } from 'react';
import { useHealth } from '@/src/hooks/useMetrics';

interface NodeCardProps {
  key?: string | number;
  id: string;
  name: string;
  status: 'ready' | 'busy' | 'offline';
  model?: string;
  ram?: string;
  colorClass: string;
  icon: ReactNode;
  onSwap?: () => void;
}

function NodeCard({ id, name, status, model, ram, colorClass, icon, onSwap }: NodeCardProps) {
  return (
    <div className="flex flex-col bg-bg-surface border border-white/5 p-3 relative overflow-hidden group min-w-[140px] flex-1">
      {/* Background flare on hover */}
      <div className={cn("absolute -inset-1 opacity-0 group-hover:opacity-10 transition-opacity blur-xl rounded-full", colorClass)} />
      
      <div className="flex items-center justify-between mb-3 z-10 relative">
        <div className="flex items-center gap-2">
          <div className={cn("w-6 h-6 flex items-center justify-center bg-black/40 border border-white/10", colorClass.replace('bg-', 'text-'))}>
            {icon}
          </div>
          <span className="text-[10px] font-mono uppercase tracking-widest font-bold text-fg1">{name}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className={cn("text-[8px] font-mono uppercase", status === 'offline' ? "text-sev-critical" : "text-fg3")}>{status}</span>
          <div className={cn(
            "w-1.5 h-1.5 rounded-full",
            status === 'ready' ? 'bg-status-confirmed' : status === 'busy' ? 'bg-status-probable animate-pulse' : 'bg-status-discarded'
          )} />
        </div>
      </div>

      <div className="flex flex-col gap-1 z-10 relative mt-auto">
        {model && (
          <div className="flex justify-between items-end">
            <span className="text-[9px] font-mono text-fg2 truncate max-w-[80px]">{model}</span>
            {ram && <span className="text-[9px] font-mono text-fg3">{ram}</span>}
          </div>
        )}
        {!model && (
           <div className="h-[14px]"></div>
        )}
      </div>

      {onSwap && (
        <button 
          onClick={onSwap}
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-black/80 px-3 py-1 border border-white/10 text-[9px] font-mono text-white hover:text-hud-cyan uppercase backdrop-blur-sm z-20"
        >
          SWAP MODEL
        </button>
      )}
    </div>
  );
}

export function NodeStatusRow() {
  const { data, error } = useHealth(5000);
  
  const resolveStatus = (nodeId: string, defaultStatus: 'ready'|'busy'|'offline'): 'ready'|'busy'|'offline' => {
    if (error) return 'offline';
    if (!data?.nodes?.[nodeId]) return defaultStatus;
    const s = data.nodes[nodeId].status;
    if (s === 'ready' || s === 'busy') return s;
    return 'offline';
  };

  const getModel = (nodeId: string, defaultModel: string) => {
    return data?.nodes?.[nodeId]?.model || defaultModel;
  };

  const nodes: NodeCardProps[] = [
    {
      id: 'tensor',
      name: 'TENSOR',
      status: resolveStatus('tensor', 'ready'),
      model: getModel('tensor', 'Llama 3.1 8B'),
      colorClass: 'bg-node-tensor',
      icon: <Network size={12} />
    },
    {
      id: 'kinetic',
      name: 'KINETIC',
      status: resolveStatus('kinetic', 'busy'),
      model: getModel('kinetic', 'Qwen2.5 3B'),
      ram: data?.nodes?.kinetic?.ram_gb ? `${data.nodes.kinetic.ram_gb}GB` : undefined,
      colorClass: 'bg-node-kinetic',
      icon: <Cpu size={12} />,
      onSwap: () => console.log('Swap KINETIC')
    },
    {
      id: 'aegis',
      name: 'AEGIS',
      status: resolveStatus('aegis', 'ready'),
      model: getModel('aegis', 'Llama 3.1 8B'),
      ram: data?.nodes?.aegis?.ram_gb ? `${data.nodes.aegis.ram_gb}GB` : undefined,
      colorClass: 'bg-node-aegis',
      icon: <ShieldAlert size={12} />,
      onSwap: () => console.log('Swap AEGIS')
    },
    {
      id: 'lattice',
      name: 'LATTICE',
      status: resolveStatus('lattice', 'ready'),
      model: data?.nodes?.lattice?.vector_count ? `${data.nodes.lattice.vector_count} Vectors` : 'Qdrant / Vector',
      colorClass: 'bg-node-lattice',
      icon: <Database size={12} />
    },
    {
      id: 'tokamak',
      name: 'TOKAMAK',
      status: resolveStatus('tokamak', 'ready'),
      model: data?.nodes?.tokamak?.active_containers ? `${data.nodes.tokamak.active_containers} Contain.` : 'Sandbox Ready',
      colorClass: 'bg-node-tokamak',
      icon: <Box size={12} />
    }
  ];

  return (
    <div className="flex gap-2 w-full overflow-x-auto pb-2 custom-scrollbar">
      {nodes.map(node => (
        <NodeCard 
          key={node.id} 
          id={node.id} 
          name={node.name} 
          status={node.status} 
          model={node.model} 
          ram={node.ram} 
          colorClass={node.colorClass} 
          icon={node.icon} 
          onSwap={node.onSwap} 
        />
      ))}
    </div>
  );
}
