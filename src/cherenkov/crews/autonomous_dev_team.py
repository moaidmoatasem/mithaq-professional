"""
Autonomous Software Development Team
A complete AI-powered development team with proper workflow
"""

import json
import os
from datetime import datetime
from typing import Dict

from crewai import LLM, Agent, Crew, Process, Task
from dotenv import load_dotenv

load_dotenv()


class AutonomousDevTeam:
    """
    Complete autonomous development team with:
    - Product Manager
    - Technical Architect
    - Tech Lead
    - Developers (parallel)
    - Code Reviewer
    - QA Tester
    - DevOps Engineer
    """

    def __init__(self, model: str = "ollama/qwen2.5:3b"):
        self.llm = LLM(model=model, base_url="http://localhost:11434")
        self.project_path = "output/autonomous_project"
        os.makedirs(self.project_path, exist_ok=True)

    def create_team(self):
        """Create all team members"""

        # 1. Product Manager - The Orchestrator
        product_manager = Agent(
            role="Product Manager",
            goal="Define roadmap, milestones, and coordinate the team",
            backstory="""You are an experienced Product Manager who creates 
            clear roadmaps with milestones and phases. You break down projects 
            into manageable tasks and track progress.""",
            llm=self.llm,
            verbose=True,
        )

        # 2. Technical Architect
        architect = Agent(
            role="Technical Architect",
            goal="Design system architecture, HLD, LLD, and design patterns",
            backstory="""You are a senior architect who creates comprehensive 
            High-Level Design (HLD) and Low-Level Design (LLD) documents. 
            You choose appropriate design patterns and ensure scalability.""",
            llm=self.llm,
            verbose=True,
        )

        # 3. Tech Lead
        tech_lead = Agent(
            role="Tech Lead",
            goal="Review code, enforce standards, approve implementations",
            backstory="""You are a technical leader who reviews all code for 
            quality, security, and best practices. You ensure the team follows 
            architectural decisions and coding standards.""",
            llm=self.llm,
            verbose=True,
        )

        # 4. Senior Developer
        senior_dev = Agent(
            role="Senior Developer",
            goal="Implement core features with high quality",
            backstory="""You are an expert developer who writes clean, 
            maintainable, production-ready code. You follow SOLID principles 
            and write comprehensive documentation.""",
            llm=self.llm,
            verbose=True,
        )

        # 5. Backend Developer
        backend_dev = Agent(
            role="Backend Developer",
            goal="Implement backend services and APIs",
            backstory="""You specialize in backend development, creating 
            robust APIs, database schemas, and business logic.""",
            llm=self.llm,
            verbose=True,
        )

        # 6. Security Developer
        security_dev = Agent(
            role="Security Developer",
            goal="Implement security features and vulnerability scanning",
            backstory="""You are a security specialist who implements 
            security controls, vulnerability scanners, and secure coding 
            practices.""",
            llm=self.llm,
            verbose=True,
        )

        # 7. Code Reviewer
        code_reviewer = Agent(
            role="Code Reviewer",
            goal="Review code for quality, security, and best practices",
            backstory="""You are a meticulous code reviewer who checks for 
            bugs, security issues, performance problems, and adherence to 
            coding standards.""",
            llm=self.llm,
            verbose=True,
        )

        # 8. QA Engineer
        qa_engineer = Agent(
            role="QA Engineer",
            goal="Write tests and ensure code quality",
            backstory="""You are a quality assurance expert who writes 
            comprehensive unit tests, integration tests, and ensures 
            test coverage meets standards.""",
            llm=self.llm,
            verbose=True,
        )

        # 9. DevOps Engineer
        devops = Agent(
            role="DevOps Engineer",
            goal="Set up CI/CD, deployment, and integration",
            backstory="""You are a DevOps expert who creates deployment 
            pipelines, manages integrations, and ensures smooth releases.""",
            llm=self.llm,
            verbose=True,
        )

        return {
            "pm": product_manager,
            "architect": architect,
            "tech_lead": tech_lead,
            "senior_dev": senior_dev,
            "backend_dev": backend_dev,
            "security_dev": security_dev,
            "reviewer": code_reviewer,
            "qa": qa_engineer,
            "devops": devops,
        }

    def create_project_workflow(self, team: Dict, project_description: str):
        """Create complete project workflow"""

        # PHASE 1: Planning & Architecture
        task_roadmap = Task(
            description=f"""Create a detailed project roadmap for: {project_description}
            
            Include:
            1. Project phases (Planning, Design, Development, Testing, Deployment)
            2. Milestones with dates
            3. Feature breakdown
            4. Success criteria
            5. Risk assessment
            
            Output a structured markdown roadmap.""",
            expected_output="Detailed project roadmap with phases and milestones",
            agent=team["pm"],
        )

        task_hld = Task(
            description=f"""Design High-Level Architecture for: {project_description}
            
            Include:
            1. System components and their responsibilities
            2. Data flow diagrams
            3. Technology stack recommendations
            4. Integration points
            5. Scalability considerations
            
            Output a comprehensive HLD document.""",
            expected_output="High-Level Design document",
            agent=team["architect"],
            context=[task_roadmap],
        )

        task_lld = Task(
            description="""Create Low-Level Design based on the HLD.
            
            Include:
            1. Class diagrams
            2. Database schema
            3. API specifications
            4. Design patterns to use (Factory, Strategy, Observer, etc.)
            5. Module structure
            
            Output detailed LLD document.""",
            expected_output="Low-Level Design document with patterns",
            agent=team["architect"],
            context=[task_hld],
        )

        # PHASE 2: Development (Parallel)
        task_core_feature = Task(
            description="""Implement the core feature based on LLD.
            
            Requirements:
            1. Follow the design patterns specified
            2. Write clean, documented code
            3. Include error handling
            4. Follow SOLID principles
            
            Output complete Python code.""",
            expected_output="Core feature implementation",
            agent=team["senior_dev"],
            context=[task_lld],
        )

        task_backend = Task(
            description="""Implement backend services and APIs based on LLD.
            
            Requirements:
            1. RESTful API endpoints
            2. Database integration
            3. Input validation
            4. Error responses
            
            Output complete backend code.""",
            expected_output="Backend service implementation",
            agent=team["backend_dev"],
            context=[task_lld],
        )

        task_security = Task(
            description="""Implement security features based on LLD.
            
            Requirements:
            1. Authentication/Authorization
            2. Input sanitization
            3. Vulnerability scanning
            4. Security middleware
            
            Output security module code.""",
            expected_output="Security implementation",
            agent=team["security_dev"],
            context=[task_lld],
        )

        # PHASE 3: Code Review
        task_review = Task(
            description="""Review all implemented code for quality and security.
            
            Check:
            1. Code follows design patterns
            2. No security vulnerabilities
            3. Proper error handling
            4. Performance optimization opportunities
            5. Code documentation
            
            Output code review report with recommendations.""",
            expected_output="Comprehensive code review report",
            agent=team["reviewer"],
            context=[task_core_feature, task_backend, task_security],
        )

        # PHASE 4: Testing
        task_testing = Task(
            description="""Write comprehensive tests for all components.
            
            Include:
            1. Unit tests for each module
            2. Integration tests
            3. Security tests
            4. Edge case tests
            
            Output complete test suite.""",
            expected_output="Complete test suite code",
            agent=team["qa"],
            context=[task_review],
        )

        # PHASE 5: Integration & Deployment
        task_integration = Task(
            description="""Create integration and deployment plan.
            
            Include:
            1. CI/CD pipeline configuration
            2. Deployment steps
            3. Rollback procedures
            4. Monitoring setup
            5. Integration checklist
            
            Output deployment guide.""",
            expected_output="Deployment and integration guide",
            agent=team["devops"],
            context=[task_testing],
        )

        # PHASE 6: Final Review by Tech Lead
        task_tech_lead_approval = Task(
            description="""Review entire project for approval.
            
            Verify:
            1. All architectural decisions followed
            2. Code quality meets standards
            3. Tests are comprehensive
            4. Documentation is complete
            5. Ready for deployment
            
            Output final approval report.""",
            expected_output="Tech lead approval and final recommendations",
            agent=team["tech_lead"],
            context=[task_integration, task_review, task_testing],
        )

        return [
            task_roadmap,
            task_hld,
            task_lld,
            task_core_feature,
            task_backend,
            task_security,
            task_review,
            task_testing,
            task_integration,
            task_tech_lead_approval,
        ]

    def run_project(self, project_description: str):
        """Run complete development project"""

        print("=" * 80)
        print("🚀 AUTONOMOUS SOFTWARE DEVELOPMENT TEAM")
        print("=" * 80)
        print(f"\nProject: {project_description}\n")

        # Create team
        print("👥 Assembling development team...")
        team = self.create_team()
        print(f"✅ Team assembled: {len(team)} members\n")

        # Create workflow
        print("📋 Creating project workflow...")
        tasks = self.create_project_workflow(team, project_description)
        print(f"✅ Workflow created: {len(tasks)} tasks\n")

        # Create crew
        crew = Crew(
            agents=list(team.values()),
            tasks=tasks,
            process=Process.sequential,  # Sequential ensures proper workflow
            verbose=True,
        )

        # Execute
        print("🎬 Starting development process...\n")
        start_time = datetime.now()

        result = crew.kickoff()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Save results
        self._save_project_outputs(result, project_description, duration)

        return result

    def _save_project_outputs(self, result, project_desc: str, duration: float):
        """Save all project outputs"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_folder = f"{self.project_path}/{timestamp}_project"
        os.makedirs(project_folder, exist_ok=True)

        # Save complete output
        with open(f"{project_folder}/complete_project.md", "w") as f:
            f.write("# Autonomous Development Project\n\n")
            f.write(f"**Project:** {project_desc}\n")
            f.write(f"**Duration:** {duration:.2f} seconds\n")
            f.write(f"**Timestamp:** {timestamp}\n\n")
            f.write("---\n\n")
            f.write(str(result))

        # Save metadata
        metadata = {
            "project": project_desc,
            "timestamp": timestamp,
            "duration_seconds": duration,
            "team_size": 9,
            "phases": [
                "Planning",
                "Architecture",
                "Development",
                "Review",
                "Testing",
                "Deployment",
            ],
        }

        with open(f"{project_folder}/metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        print("\n" + "=" * 80)
        print("✅ PROJECT COMPLETED!")
        print("=" * 80)
        print(f"📁 Output saved to: {project_folder}/")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print("👥 Team members: 9")
        print("📋 Tasks completed: 10")


if __name__ == "__main__":
    # Example usage
    team = AutonomousDevTeam()

    project = """
    Build a web vulnerability scanner with the following features:
    - XSS detection
    - SQL injection detection  
    - CSRF detection
    - Authentication bypass detection
    - RESTful API for scanning
    - Web dashboard for results
    """

    team.run_project(project)
