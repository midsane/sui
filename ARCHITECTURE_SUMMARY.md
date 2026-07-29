# Architecture Summary: Sui Execution System

## The Problem You're Facing

Currently your system can:
- ✅ Detect user intent (chat vs execute)
- ✅ Stream chat responses in real-time
- ✅ Manage conversations

But it **cannot**:
- ❌ Execute actual tasks (no tools)
- ❌ Gather missing information (incomplete requirements)
- ❌ Plan multi-step work (planner not wired)
- ❌ Handle failures gracefully (no reflection)
- ❌ Show progress (execution is opaque)
- ❌ Cancel mid-task (no interruption handling)

When a user says: **"Build a TODO app"** → Your system gets stuck.

---

## The Solution: 3 Core Pillars

### 1️⃣ **Tool System** (The Hands)
Your agent needs tools to do work:

```
┌─────────────────────────────────────┐
│         Tool Registry               │
├─────────────────────────────────────┤
│ FileTool        → read/write files  │
│ BashTool        → run commands      │
│ HttpTool        → make requests     │
│ WebSearchTool   → search web        │
│ GitTool         → version control   │
│ ... (extensible)                    │
└─────────────────────────────────────┘
        ↓
[Permission Check] [Sandbox Isolation]
```

**Key Benefit**: Safe, observable, sandboxed execution

---

### 2️⃣ **Execution Pipeline** (The Brain)
A clean orchestration of the execution flow:

```
User: "Build a website"
  ↓
[1] Requirement Gathering
    LLM: "Need more info. Which framework?"
    User: "Next.js"
    LLM: "Got it! Requirements complete."
  ↓
[2] Planning
    LLM: Creates step-by-step plan:
      Step 1: Initialize Next.js project
      Step 2: Create components
      Step 3: Add styling
      Step 4: Test & deploy
  ↓
[3] User Approval
    System: "Ready to execute? [Y/n]"
  ↓
[4] Execution (with Real-Time Feedback)
    Step 1: [Running] npx create-next-app...
    Step 1: [Done] ✓
    Step 2: [Running] Create Hero.tsx...
    Step 2: [Done] ✓
    ...
  ↓
[5] Error Recovery (Auto-Fixing)
    Step 3 Failed: npm install error
    [Reflecting] Analyzing error...
    [Retrying] Using different package version
    Step 3: [Done] ✓
  ↓
Complete! 🎉
```

**Key Benefit**: Transparent, interactive, auto-recovering

---

### 3️⃣ **Session & State Management** (The Memory)
Track everything in database:

```
Execution Session
├── id: UUID
├── task: "Build a website"
├── status: EXECUTING
├── current_step: 2/4
├── requirements: {framework: "Next.js", ...}
├── plan: ExecutionPlan(steps=[...])
├── outputs: [
│   {"step": 1, "tool": "bash", "output": "..."},
│   {"step": 2, "tool": "file_write", "output": "..."},
│   ...
│ ]
├── started_at: 2026-07-29T10:30:00Z
├── can_cancel: true
└── can_resume: true
```

**Key Benefit**: Full audit trail, resumable execution, cost tracking

---

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────┐
│                    Terminal / User Input                   │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │   Intent Router       │
         │  (Chat vs Execute)    │
         └───────────┬───────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
    ┌─────────┐          ┌─────────────────┐
    │ LLM     │          │ Execution       │
    │ Response│          │ Pipeline        │
    └────┬────┘          └────────┬────────┘
         │                        │
         │                        ▼
         │               ┌────────────────────────┐
         │               │ [1] Requirement        │
         │               │     Gatherer           │
         │               │                        │
         │               │ Asks questions until   │
         │               │ task is clear          │
         │               └────────┬───────────────┘
         │                        │
         │                        ▼
         │               ┌────────────────────────┐
         │               │ [2] Planner            │
         │               │                        │
         │               │ Creates step-by-step   │
         │               │ execution plan         │
         │               └────────┬───────────────┘
         │                        │
         │                        ▼
         │               ┌────────────────────────┐
         │               │ [3] User Approval      │
         │               │                        │
         │               │ Show plan, get OK      │
         │               └────────┬───────────────┘
         │                        │
         │                        ▼
         │               ┌────────────────────────┐
         │               │ [4] Step Executor      │
         │               │                        │
         │               │ Execute each step      │
         │               │ Call tools             │
         │               └────────┬───────────────┘
         │                        │
         │                        ▼
         │               ┌────────────────────────┐
         │               │ [5] Evaluator          │
         │               │                        │
         │               │ Did step succeed?      │
         │               │ Success? → Next step   │
         │               │ Failed?  → Reflect     │
         │               └────────┬───────────────┘
         │                        │
         │                        ▼
         │               ┌────────────────────────┐
         │               │ [6] Reflector (Optional)
         │               │                        │
         │               │ Analyze failure        │
         │               │ Generate fix           │
         │               │ Retry step             │
         │               └────────┬───────────────┘
         │                        │
         │                        ▼
         │               ┌────────────────────────┐
         │               │ Session Manager        │
         │               │                        │
         │               │ Save progress to DB    │
         │               │ Allow resume           │
         │               │ Track costs            │
         │               └────────┬───────────────┘
         │                        │
         └────────────┬──────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Terminal Output Stream │
         │                        │
         │ Real-time feedback     │
         │ Step-by-step progress  │
         │ Error messages         │
         └────────────────────────┘
```

---

## Data Flow Example: "Write a config file"

```
User Input: "Write config.yaml with database settings"
    │
    ▼
IntentRouter: EXECUTE (detected)
    │
    ▼
RequirementGatherer
    ├─ LLM: "Looks like you want config. DB type?"
    ├─ User: "PostgreSQL"
    ├─ LLM: "Host?"
    ├─ User: "localhost"
    └─ Complete! → Summary: "Write PostgreSQL config to config.yaml"
    │
    ▼
ExecutionPlanner
    ├─ LLM: Creates plan:
    │   Step 1: Validate postgres settings
    │   Step 2: Create config.yaml
    │   Step 3: Write content to file
    │   Step 4: Verify file syntax
    │
    ▼
UserApproval: Yes
    │
    ▼
StepExecutor
    ├─ Step 1: Validate
    │   └─ BashTool: psql --version
    │      Output: "psql (PostgreSQL) 15.0"
    │      Status: ✓ Success
    │
    ├─ Step 2: Create file
    │   └─ FileTool: create("config.yaml")
    │      Output: "File created at /project/config.yaml"
    │      Status: ✓ Success
    │
    ├─ Step 3: Write content
    │   └─ FileTool: write("config.yaml", content)
    │      Output: "Wrote 12 lines"
    │      Status: ✓ Success
    │
    ├─ Step 4: Verify
    │   └─ BashTool: yamllint config.yaml
    │      Output: "Valid YAML"
    │      Status: ✓ Success
    │
    ▼
ExecutionComplete
    └─ Session saved to database
       Status: COMPLETED
       Cost: $0.03 (LLM calls)
       Time: 45 seconds
       Can Resume: Yes (for future modifications)
```

---

## Key Design Decisions

| Component | Design Choice | Why |
|-----------|--------------|-----|
| **Tools** | Pluggable providers | Extensible, safe, observable |
| **Flow** | Sequential steps | Simpler to implement, debug, and understand |
| **Updates** | AsyncIterator streams | Real-time feedback, responsive UI |
| **Errors** | Auto-retry with reflection | Better UX, fewer user interventions |
| **Storage** | Full execution audit trail | Compliance, debugging, cost tracking |
| **Cancellation** | Graceful with checkpoint | No data loss, can resume |
| **Approval** | Explicit user gate | Safety, transparency, control |

---

## Why This Architecture?

### ✅ Strengths
1. **Modular**: Each component can be tested independently
2. **Extensible**: New tools don't require core changes
3. **Observable**: Real-time feedback and full audit trail
4. **Resilient**: Auto-recovery from failures
5. **Safe**: Sandboxed tools, permission gates
6. **Scalable**: Foundation for parallel execution later

### 🚨 Challenges
1. **Complexity**: More moving parts than simple LLM call
2. **Latency**: Multiple LLM calls (planning, reflection, etc.)
3. **Token Cost**: Reflection adds calls for failed steps
4. **State Management**: More state to track and persist

### 💡 How We Mitigate Challenges
- **Complexity**: Clear ADRs, comprehensive testing
- **Latency**: Cache plans, batch operations
- **Cost**: Monitor usage, optimize prompts
- **State**: Transactional DB updates, checkpoints

---

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|------------|
| 1 | Week 1 | Structured LLM output + Tools foundation |
| 2 | Week 2 | Requirements, Planning, Execution |
| 3 | Week 2-3 | Error recovery, Integration |
| 4 | Week 3 | UI polish, Testing |

**MVP Ready**: 2-3 weeks

---

## Success Definition

✅ User can request: **"Build a FastAPI project"**

System will:
1. Ask: "Need database?" → User: "PostgreSQL"
2. Ask: "Authentication?" → User: "JWT"
3. Show: 5-step plan with timestamps
4. Execute: Each step in real-time
5. Auto-fix: Failed steps
6. Complete: In 2-5 minutes
7. Save: Full audit trail

---

## Questions to Answer Before Starting

1. **Tool Priority**: File, Bash, Http for Phase 1?
2. **Approval Gates**: Always show plan before execute?
3. **Reflection Budget**: Max 2 auto-retries or more?
4. **Database**: PostgreSQL already configured?
5. **Target Workflows**: What tasks to support first?

---

## Next Actions

1. ✅ Review this architecture (you are here)
2. ⏳ Review ADRs (004, 005, 006)
3. ⏳ Approve implementation roadmap
4. ⏳ Start Phase 1 implementation
5. ⏳ Weekly demos of progress

---

## Files to Review

- `docs/adr/004_tool_system.md` — Tool architecture
- `docs/adr/005_execution_pipeline.md` — Pipeline orchestration
- `docs/adr/006_structured_llm_output.md` — LLM integration
- `IMPLEMENTATION_ROADMAP.md` — Detailed phasing
- `ARCHITECTURE_ANALYSIS.md` — Problem analysis

