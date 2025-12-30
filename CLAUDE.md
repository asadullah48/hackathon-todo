# Hackathon Todo - CLAUDE.md

## Project Context

This is a Panaversity Hackathon II project following spec-driven development.

### Current Phase: Phase 2 → Phase 3 Transition

**Phase 1**: ✅ Complete - Python CLI app  
**Phase 2**: 🔄 Backend tested, frontend testing  
**Phase 3**: 🎯 Next - MCP + OpenAI Agents + ChatKit

## SpecifyKit Plus Workflow

Always follow: Constitution → Specify → Plan → Tasks → Implement

### Constitution Location
- `.specify/memory/constitution.md` - Project principles and constraints

## Hackathon Skill Integration

**Phase 3-5 Guides**: `.claude/skills/hackathon-todo-advanced/references/`

### Key References:
- Phase 2 completion: `docs/phase-guides/phase2-completion.md`
- Phase 3 MCP setup: `docs/phase-guides/phase3-mcp-complete-guide.md`
- Phase 3 Agents SDK: `docs/phase-guides/phase3-openai-agents.md`
- Phase 3 ChatKit: `docs/phase-guides/phase3-chatkit-setup.md`
- Phase 4 K8s: `docs/phase-guides/phase4-kubernetes-local.md`
- Phase 5 Cloud: `docs/phase-guides/phase5-cloud-deployment.md`
- Bonus features: `docs/phase-guides/bonus-features.md`

### Helper Scripts:
- `scripts/tools/init_mcp_server.py` - Scaffold MCP server
- `scripts/tools/test_mcp_connection.py` - Test MCP connectivity
- `scripts/tools/generate_helm_charts.py` - Generate K8s manifests
- `scripts/tools/setup_dapr_components.py` - Create Dapr configs

## Before Starting Phase 3

1. Complete Phase 2 testing checklist: `docs/phase-guides/phase2-completion.md`
2. Ensure frontend deployed to Vercel
3. Ensure backend deployed (Railway/Render)
4. Verify Better Auth JWT working

## Starting Phase 3

1. Read: `docs/phase-guides/phase3-mcp-complete-guide.md`
2. Run: `python scripts/tools/init_mcp_server.py ./backend/mcp_server`
3. Test: `python scripts/tools/test_mcp_connection.py ./backend/mcp_server/mcp_server.py`
4. Follow OpenAI Agents SDK guide
5. Setup ChatKit with domain allowlist

## Project Structure
```
hackathon-todo/
├── .specify/              # SpecifyKit Plus
│   ├── memory/
│   │   └── constitution.md
│   └── templates/
├── .claude/
│   └── skills/
│       └── hackathon-todo-advanced/  # Phase 3-5 guides
├── docs/
│   └── phase-guides/      # Symlink to skill references
├── scripts/
│   └── tools/             # Helper scripts
├── specs/                 # Specification files
├── backend/               # FastAPI (Phase 2)
├── frontend/              # Next.js (Phase 2)
└── CLAUDE.md             # This file
```

## Development Workflow

1. **Create Spec**: `uv specifyplus specify <feature>`
2. **Generate Plan**: `uv specifyplus plan`
3. **Create Tasks**: `uv specifyplus tasks`
4. **Implement**: `uv specifyplus implement`
5. **Test**: Run tests, verify functionality
6. **Document**: Update specs and README

## Important Notes

- **No manual coding** - Always use SpecifyKit Plus workflow
- **Stateless design** - Conversation state goes in database (Phase 3+)
- **Test locally first** - Before deploying to cloud
- **Follow guides** - The skill references have complete examples

## Need Help?

1. Check the relevant phase guide in `docs/phase-guides/`
2. Review architecture diagrams in guides
3. Run diagnostic scripts when stuck
4. Consult Common Issues section in each guide
