"""
Swarm Orchestrator - Manages parallel micro agents using threading
"""
import threading
from typing import List, Dict, Any
from pathlib import Path
import json
from datetime import datetime
from queue import Queue

class MicroSwarm:
    """
    Manages parallel execution of micro agents using threads
    RAM-efficient and pickle-safe
    """
    
    def __init__(self, max_parallel: int = 4):
        self.max_parallel = max_parallel
        self.results = []
        
    def deploy(self, agents: List[Any], tasks: List[str]) -> List[Dict]:
        """
        Deploy agents in parallel using threads
        
        Args:
            agents: List of MicroAgent instances
            tasks: List of input tasks (one per agent)
        """
        print(f"\n🚀 Deploying {len(agents)} micro agents...")
        print(f"Max parallel: {self.max_parallel}")
        
        results = []
        result_queue = Queue()
        
        def worker(agent, task, index):
            """Thread worker function"""
            result = agent.execute(task)
            result['index'] = index
            result_queue.put(result)
        
        # Create and start threads
        threads = []
        for i, (agent, task) in enumerate(zip(agents, tasks)):
            thread = threading.Thread(
                target=worker,
                args=(agent, task, i)
            )
            threads.append(thread)
            thread.start()
            
            # Limit concurrent threads
            if len(threads) >= self.max_parallel:
                for t in threads:
                    t.join()
                threads = []
        
        # Wait for remaining threads
        for t in threads:
            t.join()
        
        # Collect results
        while not result_queue.empty():
            results.append(result_queue.get())
        
        # Sort by index
        results.sort(key=lambda x: x.get('index', 0))
        
        # Save results
        self._save_results(results)
        return results
    
    def _save_results(self, results: List[Dict]):
        """Save swarm results"""
        output_dir = Path("swarm_outputs")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"swarm_results_{timestamp}.json"
        
        # Remove non-serializable items
        clean_results = []
        for r in results:
            clean_r = {k: v for k, v in r.items() if k != 'index'}
            clean_results.append(clean_r)
        
        with open(output_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'total_agents': len(results),
                'successful': sum(1 for r in results if r.get('success', False)),
                'results': clean_results
            }, f, indent=2)
        
        print(f"\n✅ Results saved to {output_file}")
