#!/usr/bin/env python3
"""
mithaq CLI - Orchestration commands
"""

import click
import json
from mithaq.workflow_parser import load_workflow
from mithaq.orchestration_api import orchestrate_workflow, register_agent
from mithaq.result_persistence import ResultStore


@click.group()
def cli():
    """mithaq Orchestration CLI"""
    pass


@cli.command()
@click.option("--config", required=True, help="Workflow config file (YAML)")
@click.option("--output", default="results.json", help="Output file")
def orchestrate(config, output):
    """Run an orchestration workflow from YAML file"""
    click.echo(f"🎯 Orchestrating workflow from {config}")

    try:
        # Load workflow YAML
        workflow_config = load_workflow(config)
        click.echo(f"   Loaded: {workflow_config.get('name', 'Unnamed')}")

        # Execute workflow
        result = orchestrate_workflow(workflow_config)

        if result.success:
            # Save results
            store = ResultStore()
            store.save_result(workflow_config.get("name", "Unnamed"), result.outputs)

            click.echo(f"✅ Workflow completed in {result.duration:.2f}s")
            click.echo(f"   Results saved to {output} and result store")
        else:
            click.echo(f"❌ Workflow failed: {result.errors}")

    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
@click.option("--role", required=True, help="Agent role")
def register(role):
    """Register a new agent"""
    click.echo(f"🤖 Registering agent with role: {role}")
    try:
        # Create a mock agent object for registration
        class MockAgent:
            def __init__(self, role):
                self.role = role

        agent = MockAgent(role)
        agent_id = register_agent(agent)
        click.echo(f"✅ Agent registered successfully! ID: {agent_id.id}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")


@cli.command()
@click.option("--id", required=True, help="Workflow ID (name)")
def status(id):
    """Check workflow status"""
    click.echo(f"📊 Checking status for workflow: {id}")
    try:
        store = ResultStore()
        result = store.get_latest(id)

        if result:
            click.echo(f"✅ Latest result found for {id}:")
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"❓ No results found for workflow: {id}")
    except Exception as e:
        click.echo(f"❌ Error: {e}")


if __name__ == "__main__":
    cli()
