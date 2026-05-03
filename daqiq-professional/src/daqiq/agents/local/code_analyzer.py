"""
Local Code Analyzer Agent
Performs security-focused code analysis using local Ollama.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from daqiq.agents.local.ollama_client import OllamaClient, OllamaConfig


class CodeFile(BaseModel):
    """Represents a code file to analyze"""

    path: str
    content: str
    language: str
    size_bytes: int


class VulnerabilityFinding(BaseModel):
    """Security vulnerability finding"""

    severity: str
    category: str
    description: str
    file_path: str
    line_numbers: Optional[List[int]] = None
    remediation: str


class CodeAnalyzer:
    """
    Security-focused code analyzer using local LLM.
    100% local execution - no external API calls.
    """

    def __init__(self, ollama_config: Optional[OllamaConfig] = None):
        self.client = OllamaClient(config=ollama_config)
        self.findings: List[VulnerabilityFinding] = []

        if not self.client.is_available():
            raise RuntimeError("Ollama is not available. Please start Ollama service.")

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single code file for security issues.

        Args:
            file_path: Path to code file

        Returns:
            Analysis results
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Read file content
        content = path.read_text(encoding="utf-8", errors="ignore")

        # Detect language from extension
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".go": "go",
            ".rs": "rust",
            ".c": "c",
            ".cpp": "cpp",
            ".cs": "csharp",
            ".php": "php",
        }

        language = language_map.get(path.suffix, "unknown")

        # Analyze code
        print(f"   🔍 Analyzing {path.name} ({language})...")
        result = self.client.analyze_code(
            code=content, language=language, focus="security"
        )

        return {
            "file": str(path),
            "language": language,
            "size_bytes": len(content),
            "findings": result["findings"],
            "tokens_used": result.get("eval_tokens", 0),
        }

    def analyze_directory(
        self, directory: str, extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Analyze all code files in a directory.

        Args:
            directory: Directory path
            extensions: File extensions to analyze (e.g., ['.py', '.js'])

        Returns:
            Combined analysis results
        """

        if extensions is None:
            extensions = [".py", ".js", ".ts", ".java", ".go"]

        dir_path = Path(directory)

        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        # Find all matching files
        files = []
        for ext in extensions:
            files.extend(dir_path.rglob(f"*{ext}"))

        print(f"\n   📁 Found {len(files)} code files to analyze")

        results = []
        total_tokens = 0

        for file_path in files:
            try:
                result = self.analyze_file(str(file_path))
                results.append(result)
                total_tokens += result.get("tokens_used", 0)
            except Exception as e:
                print(f"   ⚠️  Error analyzing {file_path}: {e}")

        return {
            "directory": str(dir_path),
            "files_analyzed": len(results),
            "total_tokens": total_tokens,
            "results": results,
        }

    def quick_scan(self, code_snippet: str, language: str = "python") -> str:
        """
        Quick security scan of code snippet.

        Args:
            code_snippet: Code to analyze
            language: Programming language

        Returns:
            Security findings as string
        """

        result = self.client.analyze_code(
            code=code_snippet, language=language, focus="security"
        )

        return result["findings"]
