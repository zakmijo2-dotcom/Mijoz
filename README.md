# Unified AI Coding Agents Platform

A web-based SaaS platform that unifies multiple AI coding agent tools under a single interface with a centralized model proxy layer.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │   Claude    │ │    Codex    │ │  OpenCode   │ │ Pi Agent  │ │
│  │    Code     │ │             │ │             │ │   Tool    │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └───────────┘ │
│                          Monaco Editor + Terminal               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI/Node.js)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Model Proxy Layer (Core)                     │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐  │   │
│  │  │   Router    │ │   Fallback  │ │  Compatibility      │  │   │
│  │  │   & Load    │ │   & Retry   │ │  Shim (API Trans.)  │  │   │
│  │  │   Balancer  │ │   Logic     │ │                     │  │   │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘  │   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐   │
│  │   Auth &    │ │   Session   │ │    Key Management       │   │
│  │   RBAC      │ │   Manager   │ │    (Encrypted Store)    │   │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────────┐
│    PostgreSQL   │ │      Redis      │ │  Docker Sandboxes   │
│  (Projects,     │ │  (Queue, Cache, │ │  (Per-user/project  │
│   Sessions,     │ │   Rate Limit)   │ │   isolated exec)    │
│   Encrypted Keys)│ │                │ │                     │
└─────────────────┘ └─────────────────┘ └─────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External AI Providers                        │
│  Groq │ OpenRouter │ Google AI │ Together │ Cerebras │ Mistral │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
/workspace
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Core config, security
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic, proxy layer
│   │   └── routers/        # API routers
│   └── tests/
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities, API clients
│   │   ├── stores/        # State management
│   │   └── types/         # TypeScript types
│   └── public/
├── docker/                 # Docker configurations
├── sandbox-templates/      # Sandbox base images
└── README.md
```

## Supported AI Agents

1. **Claude Code** - Anthropic's coding assistant
2. **Codex** - OpenAI's code generation model
3. **OpenCode** - Open-source coding agent
4. **Pi Agent Tool** - Inflection's AI assistant

## Supported Model Providers (Proxy Layer)

- Groq (ultra-fast inference)
- OpenRouter (multi-model gateway)
- Google AI Studio (Gemini models)
- Together AI (open models)
- Cerebras (fast LLM inference)
- Mistral AI
- And more...

## Key Features

### Unified Agent Interface
- Single dashboard for all agents
- Embedded Monaco code editor
- Interactive terminal
- Session persistence per tool
- Mid-project agent switching

### Model Proxy Layer
- Centralized credential store
- Automatic key rotation & load balancing
- Fallback on rate limits/failures
- API compatibility shim
- Per-project routing rules

### Security
- Encrypted API key storage (AES-256)
- Docker-based sandbox isolation
- Role-based access control
- Rate limiting & audit logging

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- Docker
- PostgreSQL
- Redis

### Installation

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend setup
cd frontend
npm install

# Start services
docker-compose up -d
```

## License

MIT

## Compliance Note

⚠️ Building a proxy that mimics a provider's private API surface may violate terms of service. Review each tool's ToS before commercial deployment.
