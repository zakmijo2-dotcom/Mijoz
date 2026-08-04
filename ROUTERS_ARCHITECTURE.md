# Mijoz Router Architecture

## Overview

Mijoz now implements a sophisticated dual-router system that powers the "AI Engineering Operating System":

1. **Agent Router** - Distributes tasks to specialized AI agents
2. **Model Router** - Selects optimal models/providers for each task
3. **Docker Sandbox** - Secure isolated execution environments

---

## Agent Router

### Specialized Agents

| Agent | Role | Default Model | Capabilities |
|-------|------|---------------|--------------|
| Architect | `architect` | Claude Opus 4 | System design, technical specs |
| Developer | `developer` | Claude Sonnet 4 | Implementation, refactoring |
| Debugger | `debugger` | Claude Sonnet 4 | Bug fixing, error analysis |
| Tester | `tester` | Claude Sonnet 4 | Test generation, QA |
| Reviewer | `reviewer` | Claude Opus 4 | Code review, quality checks |
| Security Auditor | `security_auditor` | Claude Opus 4 | Security analysis, vulnerability detection |
| Documentation | `documentation` | Claude Sonnet 4 | Docs, README, guides |
| DevOps | `devops` | Claude Sonnet 4 | CI/CD, deployment, infra |

### API Endpoints

```bash
# Get all agents
GET /api/v1/agents

# Get specific agent
GET /api/v1/agents/{agent_id}

# Create custom agent
POST /api/v1/agents
{
  "name": "My Custom Agent",
  "role": "developer",
  "system_prompt": "You are...",
  "default_model": "claude-sonnet-4-20250514",
  "permissions": {...}
}

# Get dashboard stats
GET /api/v1/agents/stats

# Get active tasks
GET /api/v1/agents/active-tasks

# Route task to agent
POST /api/v1/tasks/route
{
  "task_id": "task-123",
  "task_type": "coding",
  "description": "Implement feature X",
  "complexity": 3,
  "urgency": 4
}
```

### Task Type Mapping

```python
ARCHITECTURE   → Architect
CODING         → Developer
DEBUGGING      → Debugger
TESTING        → Tester
REVIEW         → Reviewer
SECURITY       → Security Auditor
DOCUMENTATION  → Documentation
DEVOPS         → DevOps
REFACTORING    → Developer
QUICK_FIX      → Debugger
```

---

## Model Router

### Supported Providers

| Provider | Models | Speed | Quality | Cost (input/output per 1M) |
|----------|--------|-------|---------|---------------------------|
| OpenAI | gpt-4o, gpt-4o-mini | Fast | High | $5.00 / $15.00 |
| Anthropic | Claude Opus/Sonnet/Haiku | Medium | Highest | $15.00 / $75.00 |
| Google | Gemini 2.5 Pro/Flash | Fast | High | $1.25 / $5.00 |
| Groq | Llama 3.3 70B, Mixtral | **Fastest** | High | $0.59 / $0.79 |
| OpenRouter | Multi-provider | Varies | Varies | $2.50 / $2.50 |
| Together AI | Qwen Coder 32B | Fast | High | $0.18 / $0.18 |
| Cerebras | Llama 3.3 70B | **Fastest** | High | $0.90 / $0.90 |
| Mistral | Mistral Large, Codestral | Fast | High | $2.00 / $6.00 |

### Routing Strategies

```python
COST_OPTIMIZED     # Minimize cost
SPEED_OPTIMIZED    # Minimize latency
QUALITY_OPTIMIZED  # Maximize output quality
BALANCED          # Balance all factors
CONTEXT_AWARE     # Adapt based on task type
```

### Automatic Decision Factors

The Model Router considers:
- **Task complexity** - Complex tasks → higher quality models
- **Urgency** - Urgent tasks → faster models
- **Budget sensitivity** - Budget-conscious → cheaper models
- **Context size** - Large context → models with bigger windows
- **Health status** - Unhealthy providers → automatic fallback
- **Rate limits** - Approaching limits → switch to alternatives

### API Endpoints

```bash
# Get available models
GET /api/v1/models?provider=anthropic&only_healthy=true

# Get usage statistics
GET /api/v1/models/stats

# Route task to optimal model
POST /api/v1/models/route
{
  "task_id": "task-123",
  "task_type": "architecture",
  "description": "Design system architecture",
  "complexity": 5,
  "required_context": 50000
}

# Update model health
POST /api/v1/models/{provider}/{model_name}/health
{
  "success": true,
  "response_time": 1.5
}
```

### Example Routing Decision

```json
{
  "selected_model": "claude-opus-4-20250514",
  "selected_provider": "anthropic",
  "reasoning": "Selected claude-opus-4-20250514 (anthropic) for high quality output (quality tier 1) - ideal for architectural decisions (prioritized due to high urgency)",
  "estimated_cost": 0.000450,
  "estimated_time": 2.5,
  "fallback_options": [
    "openai:gpt-4o",
    "anthropic:claude-sonnet-4-20250514",
    "google:gemini-2.5-pro"
  ]
}
```

---

## Docker Sandbox Manager

### Security Features

- **Capability dropping**: All capabilities dropped by default
- **Read-only filesystem**: Prevents unauthorized modifications
- **Resource limits**: CPU, memory, disk quotas
- **Network isolation**: Optional network access per agent role
- **Command allowlisting**: Only approved commands per role
- **Audit logging**: Full command execution history

### Resource Limits (Default)

```python
CPU Limit:     2.0 cores
Memory Limit:  2GB
Disk Limit:    10GB
Timeout:       300 seconds
```

### Allowed Commands by Role

```python
Architect:     cat, ls, find, grep, head, tail
Developer:     + npm, npx, node, python, pip, git, mkdir, touch, cp, mv, rm
Debugger:      + pytest, jest, mocha
Tester:        + coverage
Security:      + audit, snyk, trivy
DevOps:        + docker, kubectl, terraform, ansible, chmod
```

### API Usage

```python
from app.sandbox.manager import sandbox_manager, SandboxConfig
from app.models.router_models import AgentRole

# Create sandbox
config = SandboxConfig(
    project_id="project-123",
    agent_role=AgentRole.DEVELOPER,
    cpu_limit=2.0,
    memory_limit="2g",
    network_enabled=False
)

session = await sandbox_manager.create_sandbox(config)

# Execute command
result = await sandbox_manager.execute_command(
    session.session_id,
    "npm install"
)

# Read file
content = await sandbox_manager.read_file(
    session.session_id,
    "/workspace/src/app.py"
)

# Write file
await sandbox_manager.write_file(
    session.session_id,
    "/workspace/src/main.py",
    "print('Hello')"
)

# Cleanup
await sandbox_manager.stop_sandbox(session.session_id)
```

### Audit Log

```bash
# Get execution history for session
GET /api/v1/sandboxes/{session_id}/history

# Get audit log for project
GET /api/v1/sandboxes/audit?project_id=project-123
```

---

## Agent Pipelines

For complex tasks requiring multiple agents:

```python
from app.services.agent_router import agent_router
from app.models.router_models import AgentRole

# Create pipeline
pipeline = agent_router.create_agent_pipeline(
    task_description="Build complete authentication system",
    pipeline_roles=[
        AgentRole.ARCHITECT,      # Design the system
        AgentRole.DEVELOPER,      # Implement
        AgentRole.TESTER,         # Write tests
        AgentRole.SECURITY_AUDITOR,  # Security review
        AgentRole.REVIEWER        # Final code review
    ]
)

# Execute pipeline
result = await agent_router.execute_pipeline(
    pipeline,
    initial_context={
        "requirements": "...",
        "tech_stack": ["FastAPI", "PostgreSQL", "JWT"]
    }
)
```

---

## Dashboard Integration

### Real-time Stats

```javascript
// Agent stats
GET /api/v1/agents/stats

Response:
{
  "total_agents": 8,
  "idle_agents": 5,
  "busy_agents": 3,
  "error_agents": 0,
  "active_tasks": 3,
  "total_tasks_processed": 1247,
  "successful_tasks": 1235,
  "failed_tasks": 12,
  "success_rate": 99.04
}

// Model stats
GET /api/v1/models/stats

Response:
{
  "total_requests": 5432,
  "total_cost": 12.45,
  "total_tokens_input": 2500000,
  "total_tokens_output": 750000,
  "models_used": 8
}
```

---

## Implementation Status

| Component | Status | Tests | Docs |
|-----------|--------|-------|------|
| Agent Router | ✅ Complete | ⏳ Pending | ✅ Complete |
| Model Router | ✅ Complete | ⏳ Pending | ✅ Complete |
| Docker Sandbox | ✅ Complete | ⏳ Pending | ✅ Complete |
| API Endpoints | ✅ Complete | ⏳ Pending | ✅ Complete |
| Frontend Integration | ⏳ In Progress | - | - |

---

## Next Steps

1. **Frontend Dashboard** - Real-time agent/model monitoring UI
2. **Agent Execution Engine** - Connect routers to actual LLM execution
3. **Enhanced Security** - Seccomp profiles, user namespaces
4. **Database Integration** - Persist agent configs, task history
5. **WebSocket Support** - Real-time streaming for agent outputs
6. **Marketplace** - Custom agent templates sharing

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                     User Request                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Agent Router                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Specialized Agents:                            │   │
│  │  Architect • Developer • Debugger • Tester      │   │
│  │  Reviewer • Security • Docs • DevOps            │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Model Router                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Providers: OpenAI • Anthropic • Google • Groq  │   │
│  │  OpenRouter • Together • Cerebras • Mistral     │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Docker Sandbox                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Isolated Containers per Agent:                 │   │
│  │  • Resource Limits                              │   │
│  │  • Command Allowlisting                         │   │
│  │  • Audit Logging                                │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Compliance Note

⚠️ **Important**: The Model Router uses official public APIs only. Ensure compliance with each provider's Terms of Service:
- Use official API endpoints
- Respect rate limits and quotas
- Do not attempt to bypass authentication
- Follow acceptable use policies

The Agent Router is designed to work with authorized tools and frameworks only.
