# Unified AI Coding Agents Platform

A web-based SaaS platform that unifies multiple AI coding agent tools under a single interface with a centralized model proxy layer.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)
![Docker](https://img.shields.io/badge/docker-enabled-blue.svg)

## 🌟 Features

### Unified Agent Interface
- **Single Dashboard** - Access Claude Code, Codex, OpenCode, and Pi Agent from one place
- **Embedded Monaco Editor** - Professional code editing with syntax highlighting
- **Interactive Terminal** - Execute commands in isolated Docker sandboxes
- **Session Persistence** - Maintain context per tool and project
- **Mid-Project Agent Switching** - Change agents without losing work

### Model Proxy Layer (Core Innovation)
- **Multi-Provider Support** - Groq, OpenRouter, Google AI, Together AI, Cerebras, Mistral, Anthropic, OpenAI
- **Automatic Fallback** - Seamlessly switch providers on rate limits or failures
- **Load Balancing** - Distribute requests across multiple API keys
- **API Compatibility Shim** - Translate between different provider formats transparently
- **Per-Project Routing** - Define rules like "use Groq for fast iteration, stronger models for review"

### Security First
- **Encrypted Key Storage** - AES-256 encryption for all API keys at rest
- **Docker Sandbox Isolation** - Per-user/per-project execution environments
- **Role-Based Access Control** - Fine-grained permissions
- **Rate Limiting & Audit Logs** - Full request tracking and protection

## 🏗 Architecture

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
│                    Backend (FastAPI/Python)                     │
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

## 📁 Project Structure

```
/workspace
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── core/           # Config, security, encryption
│   │   ├── models/         # Database schemas
│   │   ├── services/       # Business logic, proxy layer
│   │   └── routers/        # API route handlers
│   └── tests/
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router pages
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities, API clients
│   │   ├── stores/        # State management (Zustand)
│   │   └── types/         # TypeScript definitions
│   └── public/
├── docker/                 # Docker configurations
├── sandbox-templates/      # Secure sandbox base images
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Docker** & Docker Compose
- **Node.js** 18+ (for local frontend development)
- **Python** 3.10+ (for local backend development)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/zakmijo2-dotcom/Mijoz.git
cd Mijoz

# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Build and start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp ../.env.example .env
# Edit .env with your settings

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend setup (in new terminal)
cd frontend
npm install
npm run dev

# Start supporting services (PostgreSQL, Redis)
docker-compose up -d postgres redis
```

## 🔧 Configuration

See `.env.example` for all available environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/ai_agents` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT signing key (min 32 chars) | _change in production_ |
| `ENCRYPTION_KEY` | API key encryption key (32 chars) | _change in production_ |
| `SANDBOX_TEMPLATE` | Docker sandbox image | `ai-agents-sandbox:latest` |
| `RATE_LIMIT_PER_MINUTE` | Max requests per minute | `60` |

## 🤖 Supported Agents

| Agent | Description | Status |
|-------|-------------|--------|
| **Claude Code** | Anthropic's coding assistant | ✅ Supported |
| **Codex** | OpenAI's code generation model | ✅ Supported |
| **OpenCode** | Open-source coding agent | ✅ Supported |
| **Pi Agent Tool** | Inflection's AI assistant | ✅ Supported |

## 🌐 Supported Model Providers

| Provider | Models | Speed | Cost |
|----------|--------|-------|------|
| **Groq** | Llama, Mixtral | ⚡⚡⚡ Ultra-fast | $ |
| **OpenRouter** | 50+ models | ⚡⚡ Fast | $$ |
| **Google AI** | Gemini Pro/Flash | ⚡⚡ Fast | $ |
| **Together AI** | Open source models | ⚡⚡ Fast | $ |
| **Cerebras** | Various LLMs | ⚡⚡⚡ Ultra-fast | $ |
| **Mistral AI** | Mistral, Mixtral | ⚡⚡ Fast | $$ |
| **Anthropic** | Claude family | ⚡ Standard | $$$ |
| **OpenAI** | GPT-4, GPT-3.5 | ⚡ Standard | $$$ |

## 🛡 Security Considerations

### Sandbox Isolation
- Each user/project runs in an isolated Docker container
- Non-root user execution (`sandbox` user, UID 1000)
- Network isolation via dedicated Docker network
- Resource limits to prevent abuse

### API Key Protection
- All provider keys encrypted at rest using Fernet (AES-128-CBC)
- Keys decrypted only in memory during request processing
- Never logged or exposed in responses

### Compliance Notice
> ⚠️ **Important**: Building a proxy that mimics a provider's private API surface may violate terms of service. This platform is designed for educational purposes and legitimate use cases. Always review each tool's ToS and API usage policy before commercial deployment.

## 📊 Roadmap

### Phase 1: Foundation (Current)
- ✅ Core proxy layer with 8 providers
- ✅ Basic authentication & encryption
- ✅ Frontend dashboard shell
- ✅ Docker sandbox templates

### Phase 2: Production Ready
- [ ] Complete authentication flow
- [ ] Project & session management
- [ ] Real-time terminal integration
- [ ] Monaco editor integration
- [ ] Comprehensive test suite

### Phase 3: Advanced Features
- [ ] Multi-agent collaboration
- [ ] Custom agent plugins
- [ ] Usage analytics & billing
- [ ] Team collaboration features
- [ ] VS Code extension

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test
```

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📬 Contact

- **GitHub**: [@zakmijo2-dotcom](https://github.com/zakmijo2-dotcom)
- **Project Link**: [https://github.com/zakmijo2-dotcom/Mijoz](https://github.com/zakmijo2-dotcom/Mijoz)

---

**Built with ❤️ using FastAPI, Next.js, and Docker**
