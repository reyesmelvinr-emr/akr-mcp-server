What’s New in Agent Skills: Code Skills, Script Execution, and Approval for Python
Date: 13 March 2026

Code-Defined Skills, Script Execution, and Approval for Agent Skills in Python
When we introduced Agent Skills for Microsoft Agent Framework, you could package domain expertise as file-based skill directories and have agents discover and load them on demand. Now, the Python SDK takes skills further — you can define skills entirely in code, let agents execute scripts bundled with skills, and gate script execution behind human approval. These additions give you more flexibility in how you author skills, more power in what agents can do with them, and more control over when agents are allowed to act.

Code-Defined Skills
Until now, every skill started as a directory on the filesystem with a SKILL.md file. That works well for static, shareable knowledge packages, but not every skill fits that mold. Sometimes skill content comes from a database. Sometimes you want skill definitions to live alongside the application code that uses them. And sometimes a resource needs to execute logic at read time rather than serve static text.

Code-defined skills address these scenarios. You create a Skill instance in Python with a name, description, and instruction content — no files required:

Copy
from textwrap import dedent
from agent_framework import Skill, SkillResource, SkillsProvider

code_style_skill = Skill(
    name="code-style",
    description="Coding style guidelines and conventions for the team",
    content=dedent("""\
        Use this skill when answering questions about coding style,
        conventions, or best practices for the team.
    """),
    resources=[
        SkillResource(
            name="style-guide",
            content=dedent("""\
                # Team Coding Style Guide
                - Use 4-space indentation (no tabs)
                - Maximum line length: 120 characters
                - Use type annotations on all public functions
            """),
        ),
    ],
)

skills_provider = SkillsProvider(skills=[code_style_skill])
The agent uses code-defined skills exactly like file-based ones — calling load_skill to retrieve instructions and read_skill_resource to fetch resources. From the agent’s perspective, there’s no difference.

Dynamic Resources
Static content is useful, but sometimes you need resources that return fresh data each time they’re read. The @skill.resource decorator registers a function as a resource. Both sync and async functions are supported:

Copy
import os
from agent_framework import Skill

project_info_skill = Skill(
    name="project-info",
    description="Project status and configuration information",
    content="Use this skill for questions about the current project.",
)

@project_info_skill.resource
def environment() -> Any:
    """Get current environment configuration."""
    env = os.environ.get("APP_ENV", "development")
    region = os.environ.get("APP_REGION", "us-east-1")
    return f"Environment: {env}, Region: {region}"

@project_info_skill.resource(name="team-roster", description="Current team members")
def get_team_roster() -> Any:
    """Return the team roster."""
    return "Alice Chen (Tech Lead), Bob Smith (Backend Engineer)"
When the decorator is used without arguments (@skill.resource), the function name becomes the resource name and the docstring becomes the description. Use @skill.resource(name="...", description="...") to set them explicitly. The function is called each time the agent reads the resource, so it can pull up-to-date data from databases, APIs, or environment variables.

Code-Defined Scripts
Use the @skill.script decorator to register a function as an executable script on a skill. Code-defined scripts run in-process as direct function calls:

Copy
from agent_framework import Skill

unit_converter_skill = Skill(
    name="unit-converter",
    description="Convert between common units using a conversion factor",
    content="Use the convert script to perform unit conversions.",
)

@unit_converter_skill.script(name="convert", description="Convert a value: result = value × factor")
def convert_units(value: float, factor: float) -> str:
    """Convert a value using a multiplication factor."""
    import json
    result = round(value * factor, 4)
    return json.dumps({"value": value, "factor": factor, "result": result})
A JSON Schema is automatically created from the function’s typed parameters and presented to the agent, so it knows what arguments the script expects and provides them accordingly when calling run_skill_script.

Combining File-Based and Code-Defined Skills
You can mix both approaches in a single SkillsProvider. Pass skill_paths for file-based skills and skills for code-defined ones. If a code-defined skill shares a name with a file-based skill, the file-based version takes precedence:

Copy
from pathlib import Path
from agent_framework import Skill, SkillsProvider

my_skill = Skill(
    name="my-code-skill",
    description="A code-defined skill",
    content="Instructions for the skill.",
)

skills_provider = SkillsProvider(
    skill_paths=Path(__file__).parent / "skills",
    skills=[my_skill],
)
Script Execution
Skills can include executable scripts that the agent runs via the run_skill_script tool. How a script runs depends on how it was defined:

Code-defined scripts (registered via @skill.script) run in-process as direct function calls. No runner is needed.
File-based scripts (.py files discovered in skill directories) require a SkillScriptRunner — any callable matching (skill, script, args) -> Any — that you provide to control how the script is executed.
To enable execution of file-based scripts, pass a script_runner to SkillsProvider:

Copy
from pathlib import Path
from agent_framework import Skill, SkillScript, SkillsProvider

def my_runner(skill: Skill, script: SkillScript, args: dict | None = None) -> str:
    """Run a file-based script as a subprocess."""
    import subprocess, sys
    cmd = [sys.executable, str(Path(skill.path) / script.path)]
    if args:
        for key, value in args.items():
            if value is not None:
                cmd.extend([f"--{key}", str(value)])
    # ... Execute cmd in a sandboxed subprocess and return stdout
    return result.stdout.strip()

skills_provider = SkillsProvider(
    skill_paths=Path(__file__).parent / "skills",
    script_runner=my_runner,
)
This runner is provided for demonstration purposes only. For production use, implement proper sandboxing, resource limits, input validation, and structured logging.
The runner receives the resolved Skill, SkillScript, and an optional args dictionary. You control the execution environment — how scripts are launched, what permissions they have, and how their output is captured.

Script Approval
When agents can execute scripts, you need a way to keep a human in the loop for sensitive operations. Setting require_script_approval=True on SkillsProvider gates all script execution behind human approval. Instead of executing immediately, the agent pauses and returns approval requests that your application handles:

Copy
from agent_framework import Agent, Skill, SkillsProvider

# Create provider with approval enabled
skills_provider = SkillsProvider(
    skills=[my_skill],
    require_script_approval=True,
)

# ... Create an agent with skills_provider as a context provider and start a session
result = await agent.run("Deploy version 2.5.0 to production", session=session)

# Handle approval requests
while result.user_input_requests:
    for request in result.user_input_requests:
        print(f"Script: {request.function_call.name}")
        print(f"Args: {request.function_call.arguments}")

        approval = request.to_function_approval_response(approved=True)
        result = await agent.run(approval, session=session)
When a script is rejected (approved=False), the agent is informed that the user declined and can respond accordingly — explaining the limitation or suggesting an alternative approach.

This pattern gives you the benefits of agent-driven script execution while maintaining the oversight that enterprise environments require.

Use Cases
Data Validation Pipelines
Package your organization’s data quality rules as a skill with validation scripts. When an analyst asks the agent to check a dataset, it loads the skill, runs the validation script against the data, and reports results — all following the same rules every time. With approval enabled, a data steward can review each validation before it executes.

DevOps Runbooks
Turn your team’s operational procedures into skills with executable scripts for common tasks like log retrieval, health checks, or configuration changes. The agent loads the right runbook based on the issue, and the approval mechanism ensures that no deployment or infrastructure change happens without human sign-off.

Dynamic Knowledge from Internal Systems
Use code-defined skills with dynamic resources to surface live information from internal APIs, databases, or configuration systems. An HR agent can pull current policy details from a CMS at read time rather than relying on a static copy that might be stale.

Security Considerations
Script execution introduces additional responsibility. Agent Skills should be treated like any third-party code you bring into your project:

Review before use — Read all skill content and scripts before deploying. Verify that a script’s actual behavior matches its stated intent.
Sandbox execution — Run file-based scripts in isolated environments. Limit filesystem, network, and system-level access to only what the skill requires.
Use approval for sensitive operations — Enable require_script_approval=True for any skill that can produce side effects in production systems.
Audit and log — Record which skills are loaded, which scripts are executed, and what arguments are passed to maintain an audit trail.