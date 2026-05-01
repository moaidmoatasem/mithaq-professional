"""
Base MicroGPT Agent - Single purpose, minimal memory
"""
from typing import Callable, Any
from pydantic import BaseModel, Field
import time

class MicroAgentConfig(BaseModel):
    """Strict config for micro agents"""
    role: str = Field(..., description="Single-word role")
    purpose: str = Field(..., description="One sentence purpose")
    tool_function: Callable = Field(..., description="Single tool to use")
    
    class Config:
        arbitrary_types_allowed = True

class MicroAgent:
    """
    Ultra-lightweight agent with ONE tool and ONE purpose
    Runs fast, uses minimal RAM, fail-closed design
    """
    
    def __init__(self, config: MicroAgentConfig):
        self.config = config
        
    def execute(self, input_data: str) -> dict:
        """Execute single-purpose task"""
        start = time.time()
        
        print(f"  🤖 {self.config.role} processing...")
        
        try:
            # Call the tool function directly (no LLM overhead)
            result = self.config.tool_function(input_data)
            
            return {
                'success': True,
                'result': result,
                'duration': time.time() - start,
                'agent': self.config.role
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'duration': time.time() - start,
                'agent': self.config.role
            }
