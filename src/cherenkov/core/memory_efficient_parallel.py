"""
Memory-Efficient Parallel Agent Execution
Batched processing with aggressive memory cleanup
"""

from crewai import Agent, Task, Crew, Process, LLM
from typing import List, Dict, Any
import gc
import os
from datetime import datetime


class MemoryEfficientCrew:
    """Execute agents in memory-efficient batches"""

    def __init__(self, model: str = "ollama/qwen2.5:3b", batch_size: int = 2):
        """
        Initialize memory-efficient crew

        Args:
            model: Ollama model name
            batch_size: Number of tasks per batch (2 recommended for 8GB RAM)
        """
        self.model = model
        self.batch_size = batch_size
        # Single shared LLM instance (saves RAM)
        self.llm = LLM(model=model, base_url="http://localhost:11434")
        self.results = []

    def create_agent(self, config: Dict[str, Any]) -> Agent:
        """Create a single agent with shared LLM"""
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            llm=self.llm,  # Reuse same model instance
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", False),
        )

    def create_task(self, config: Dict[str, Any], agent: Agent) -> Task:
        """Create a task for an agent"""
        return Task(
            description=config["description"],
            expected_output=config["expected_output"],
            agent=agent,
        )

    def run_batch(
        self, batch_agents: List[Dict], batch_tasks: List[Dict], batch_num: int
    ):
        """Execute a single batch of agents/tasks"""
        print("\n" + "=" * 70)
        print(f"📦 BATCH {batch_num}")
        print("=" * 70)
        print(f"Tasks in this batch: {len(batch_tasks)}")

        # Create agents for this batch
        agents = [self.create_agent(cfg) for cfg in batch_agents]

        # Create tasks
        tasks = [
            self.create_task(task_cfg, agents[i])
            for i, task_cfg in enumerate(batch_tasks)
        ]

        # Execute batch
        crew = Crew(
            agents=agents, tasks=tasks, process=Process.sequential, verbose=True
        )

        start_time = datetime.now()
        result = crew.kickoff()
        duration = (datetime.now() - start_time).total_seconds()

        print(f"\n✅ Batch {batch_num} completed in {duration:.1f}s")

        # Aggressive memory cleanup
        del crew, agents, tasks
        gc.collect()

        return {"batch_num": batch_num, "result": result, "duration": duration}

    def run_parallel_batches(
        self, agent_configs: List[Dict], task_configs: List[Dict]
    ) -> List[Dict]:
        """
        Run all tasks in batches with memory cleanup

        Args:
            agent_configs: List of agent configurations
            task_configs: List of task configurations

        Returns:
            List of batch results
        """
        print("\n" + "=" * 70)
        print("🚀 MEMORY-EFFICIENT PARALLEL EXECUTION")
        print("=" * 70)
        print(f"Total agents: {len(agent_configs)}")
        print(f"Total tasks: {len(task_configs)}")
        print(f"Batch size: {self.batch_size}")
        print(f"Model: {self.model}")

        # Calculate number of batches
        num_batches = (len(task_configs) + self.batch_size - 1) // self.batch_size
        print(f"Number of batches: {num_batches}")

        results = []

        # Process in batches
        for i in range(0, len(task_configs), self.batch_size):
            batch_num = (i // self.batch_size) + 1

            # Get batch slice
            batch_tasks = task_configs[i : i + self.batch_size]
            batch_agents = agent_configs[i : i + self.batch_size]

            # Run batch
            batch_result = self.run_batch(batch_agents, batch_tasks, batch_num)
            results.append(batch_result)

            # Show progress
            print(f"\n📊 Progress: {batch_num}/{num_batches} batches complete")

        print("\n" + "=" * 70)
        print("✅ ALL BATCHES COMPLETED!")
        print("=" * 70)

        total_duration = sum(r["duration"] for r in results)
        print(f"⏱️  Total time: {total_duration:.1f}s")
        print(f"💾 Memory cleaned after each batch")

        return results

    def save_results(self, results: List[Dict], output_dir: str = "output/batched"):
        """Save batch results to files"""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for result in results:
            filename = f"{output_dir}/batch_{result['batch_num']}_{timestamp}.txt"
            with open(filename, "w") as f:
                f.write(f"Batch: {result['batch_num']}\n")
                f.write(f"Duration: {result['duration']:.1f}s\n")
                f.write("=" * 70 + "\n")
                f.write(str(result["result"]))

            print(f"📄 Saved: {filename}")


if __name__ == "__main__":
    # Quick test
    crew = MemoryEfficientCrew(batch_size=2)

    agents = [
        {"role": "Test Dev 1", "goal": "Test goal 1", "backstory": "Expert 1"},
        {"role": "Test Dev 2", "goal": "Test goal 2", "backstory": "Expert 2"},
    ]

    tasks = [
        {"description": "Write hello world", "expected_output": "Code"},
        {"description": "Write goodbye world", "expected_output": "Code"},
    ]

    results = crew.run_parallel_batches(agents, tasks)
    crew.save_results(results)
