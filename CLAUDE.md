# Hackathon Todo - Claude Code Instructions

## Project Context

This is a **Panaversity Hackathon II** project following **spec-driven development** with SpecifyKit Plus.

### Current Status

**Phase 1**: ✅ Complete - Python CLI app tested  
**Phase 2**: 🔄 Backend tested, Frontend in testing  
**Phase 3**: 🎯 Next - MCP + OpenAI Agents + ChatKit

## SpecifyKit Plus Workflow

**Always follow**: Constitution → Specify → Plan → Tasks → Implement

- **Constitution**: `.specify/memory/constitution.md`
- **Commands**: Use `uv specifyplus` commands

## Hackathon Phase Guides

**Location**: `.claude/skills/hackathon-todo-advanced/references/`  
**Quick Access**: `docs/phase-guides/`

### Phase Guides:
- ✅ **Phase 2 Completion**: `docs/phase-guides/phase2-completion.md`
- 🎯 **Phase 3 MCP Server**: `docs/phase-guides/phase3-mcp-complete-guide.md`
- 🎯 **Phase 3 OpenAI Agents**: `docs/phase-guides/phase3-openai-agents.md`
- 🎯 **Phase 3 ChatKit Setup**: `docs/phase-guides/phase3-chatkit-setup.md`
- 📦 **Phase 4 Kubernetes**: `docs/phase-guides/phase4-kubernetes-local.md`
- ☁️ **Phase 5 Cloud Deploy**: `docs/phase-guides/phase5-cloud-deployment.md`
- 🏆 **Bonus Features** (+600pts): `docs/phase-guides/bonus-features.md`

### Helper Scripts:
- `scripts/tools/init_mcp_server.py` - Scaffold MCP server
- `scripts/tools/test_mcp_connection.py` - Test MCP connectivity
- `scripts/tools/generate_helm_charts.py` - Generate Helm charts
- `scripts/tools/setup_dapr_components.py` - Create Dapr configs

## Before Starting Phase 3

1. **Complete Phase 2**: Check `docs/phase-guides/phase2-completion.md`
2. **Deploy Frontend**: Vercel
3. **Deploy Backend**: Railway/Render
4. **Verify Better Auth**: JWT tokens working

## Starting Phase 3 (When Ready)
```bash
# 1. Read the MCP guide
code docs/phase-guides/phase3-mcp-complete-guide.md

# 2. Initialize MCP server
python scripts/tools/init_mcp_server.py ./backend/mcp_server

# 3. Test MCP connection
python scripts/tools/test_mcp_connection.py ./backend/mcp_server/mcp_server.py

# 4. Follow Agents SDK guide
code docs/phase-guides/phase3-openai-agents.md

# 5. Setup ChatKit
code docs/phase-guides/phase3-chatkit-setup.md
```

## Project Structure
```
hackathon-todo/
├── .specify/              # SpecifyKit Plus
│   ├── memory/constitution.md
│   └── templates/
├── .claude/
│   └── skills/
│       └── hackathon-todo-advanced/
│           ├── SKILL.md
│           ├── references/    # 📚 Phase guides
│           └── scripts/       # 🔧 Tools
├── docs/
│   └── phase-guides/         # → Quick access symlink
├── scripts/
│   └── tools/                # Helper scripts
├── specs/                    # Spec files
├── backend/                  # FastAPI
├── frontend/                 # Next.js
└── CLAUDE.md                # This file
```

## Development Principles

1. **Spec-Driven**: No manual coding - use SpecifyKit Plus
2. **Stateless Backend**: Store conversation state in database (Phase 3+)
3. **Test Locally**: Before cloud deployment
4. **Follow Guides**: Complete examples in phase-guides/

## Need Help?

1. Check relevant guide in `docs/phase-guides/`
2. Review "Common Issues" section
3. Run diagnostic scripts
4. Check architecture diagrams

Good luck! 🚀
