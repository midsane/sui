# Sui Execution Architecture Analysis & Design

## Current State Analysis

### What Works Well ✅
- Clean entity separation (Agents, Conversations, Messages, Executions)
- Intent router correctly identifies chat vs execution
- LLM abstraction with multiple providers (Gemini, OpenAI, OpenRouter)
- Database models prepared for execution tracking
- Terminal UI with streaming capabilities

### Critical Issues 🚨

#### 1. **Incomplete Execution Pipeline**
- `ExecutionService.execute()` is a stub returning placeholder text
- No requirements gathering despite schema existing
- No planning component despite scaffolding
- No step-by-step execution or tool invocation
- No feedback mechanism for long-running tasks

#### 2. **Missing Tool System**
- No tool abstraction layer (MCP-like)
- No built-in tools (file I/O, bash, http, etc.)
- No tool permission model
- No sandboxing or safety constraints

#### 3. **LLM Service Limitations**
- `RequirementAgent` calls `llm_call()` with `response_schema` but LLMService doesn't support structured output
- No retry logic for failed calls
- No cost tracking per execution
- Limited error handling

#### 4. **Session & State Management**
- No execution session tracking
- No way to track intermediate steps or outputs
- State machine incomplete (states defined but not used)
- No cancellation mechanism

#### 5. **Missing Components**
- Requirement gathering incomplete
- Planner not implemented
- Evaluator not implemented
- Reflection/retry logic missing
- No step runner for execution

#### 6. **Database Disconnects**
- Execution model exists but not integrated into service layer
- No execution repository
- Logs stored as JSONB but not used
- Token tracking not wired up

---

## Proposed Architecture

```
User Input (Terminal)
    │
    ▼
Intent Router (Chat vs Execute)
    │
    ├─── CHAT ──────────────────────→ LLM Service → Stream Response
    │
    └─── EXECUTE ─────────────────────→ Execution Pipeline
                                              │
                                              ▼
                                    Requirements Gatherer
                                              │
                                              ├─ Needs Input? ─→ Ask User
                                              │                     │
                                              └─ Complete? ────────┘
                                              │
                                              ▼
                                         Planner
                                              │
                                              ▼
                                    User Approval
                                              │
                                              ▼
                                      Step Executor
                                     ┌────────┴────────┐
                                     ▼                 ▼
                                 Tool Call         Evaluate
                                     │                 │
                                     └────────┬────────┘
                                              ▼
                                           Success?
                                          /        \
                                       Yes         No
                                        │           │
                                        ▼           ▼
                                     Next Step    Reflector
                                        │           │
                                        │      Generate Fix
                                        │           │
                                        └─────┬─────┘
                                              ▼
                                         More Steps?
                                          /        \
                                       Yes         No
                                        │           │
                                        └─────┬─────┘
                                              ▼
                                          Complete
```

### Core Components

#### 1. **Tool System** (MCP-inspired)
```
IToolProvider (Interface)
├── FileTool (read, write, list)
├── BashTool (execute commands)
├── HttpTool (make requests)
├── WebSearchTool (search web)
├── GitTool (git operations)
└── ToolRegistry (discovery, permissions)
```

#### 2. **Execution Pipeline**
```
ExecutionService (Orchestrator)
├── RequirementGatherer
├── ExecutionPlanner
├── StepExecutor
├── Evaluator
├── Reflector
└── ExecutionSessionManager
```

#### 3. **Session Management**
```
ExecutionSession
├── id (UUID)
├── task (str)
├── requirements (dict)
├── plan (ExecutionPlan)
├── current_step_index (int)
├── status (ExecutionStatus)
├── outputs (list[StepOutput])
└── can_cancel (bool)
```

#### 4. **State Machine**
```
INIT
  ↓
GATHERING_REQUIREMENTS
  ├─ NEEDS_INPUT (wait for user) → back to GATHERING_REQUIREMENTS
  └─ COMPLETE
      ↓
    PLANNING
      ↓
    AWAITING_APPROVAL
      ├─ APPROVED
      │   ↓
      │ EXECUTING
      │   ├─ STEP_EXECUTING
      │   ├─ STEP_EVALUATING
      │   ├─ STEP_SUCCESS → next step or COMPLETED
      │   └─ STEP_FAILED → REFLECTING
      │       └─ (generates fix) → back to EXECUTING
      └─ REJECTED
          ↓
        FAILED
```

---

## Implementation Strategy

### Phase 1: Tool System Foundation
1. Create `IToolProvider` interface
2. Implement core tools (file, bash, http)
3. Build `ToolRegistry` with permission checks
4. Create `ToolContext` for execution environment

### Phase 2: Execution Session & State Management
1. Build `ExecutionSession` model + repository
2. Implement state machine in `ExecutionStateManager`
3. Add cancellation mechanism
4. Create `ExecutionOutputStore` for step results

### Phase 3: Pipeline Components
1. **RequirementGatherer**: Structured output from LLM
2. **ExecutionPlanner**: Convert requirements → step plan
3. **StepExecutor**: Run tools based on plan
4. **Evaluator**: Verify step success
5. **Reflector**: Fix failures

### Phase 4: Service Integration
1. Update `ExecutionService` to orchestrate pipeline
2. Connect to `ExecutionRepository` for persistence
3. Stream all updates to terminal
4. Handle user interrupts

### Phase 5: User Experience
1. Show gathering progress
2. Display plan before execution
3. Approval UI
4. Real-time step updates
5. Error recovery UI

---

## Database Schema Updates

```sql
-- execution_sessions
CREATE TABLE execution_sessions (
    id UUID PRIMARY KEY,
    execution_id UUID FOREIGN KEY,
    status ExecutionStatus,
    requirements JSONB,
    plan JSONB,
    current_step_index INT,
    outputs JSONB[],
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    cancelled_at TIMESTAMP
);

-- step_outputs (logs from each step)
CREATE TABLE step_outputs (
    id UUID PRIMARY KEY,
    session_id UUID FOREIGN KEY,
    step_index INT,
    tool_name VARCHAR,
    tool_input JSONB,
    tool_output JSONB,
    status StepStatus,
    error_message TEXT,
    created_at TIMESTAMP
);

-- tool_usage (for monitoring & costs)
CREATE TABLE tool_usage (
    id UUID PRIMARY KEY,
    session_id UUID FOREIGN KEY,
    tool_name VARCHAR,
    usage_count INT,
    tokens_used INT,
    cost DECIMAL,
    created_at TIMESTAMP
);
```

---

## Key Design Decisions

### 1. **Async-First Streaming**
- All operations are `AsyncIterator[str]` for real-time feedback
- Terminal receives live updates as they happen
- User can interrupt at any time

### 2. **Composable Tool System**
- Tools are discoverable and chainable
- Each tool has clear input/output schema
- Permissions checked before execution
- Sandboxing built into tool implementations

### 3. **Explicit Approval Gates**
- Show plan before execution starts
- User must approve execution
- Can inspect all tool calls before they run

### 4. **Reflection Loop**
- Failed steps trigger reflection
- LLM generates fixes automatically
- Limited retry attempts to prevent infinite loops
- User can manually override

### 5. **Complete Observability**
- Every step logged to database
- Cost tracking per tool call
- Token usage monitored
- Execution can be resumed from checkpoints

### 6. **Graceful Degradation**
- Missing tools don't crash execution
- Execution continues if non-critical step fails
- User can manually fix and resume
- No data loss on cancellation

---

## Future Extensions

### Not in Phase 1 but planned:
1. **Multi-Agent Execution**: Multiple agents working in parallel
2. **Event-Driven**: Use task queues for async execution
3. **Sandboxed Code Execution**: Run user code safely
4. **Agent Autonomy Levels**: User-configurable automation
5. **Knowledge Base Integration**: Learn from past executions
6. **Cost Optimization**: Minimize LLM calls through caching
7. **Distributed Execution**: Run on remote workers

---

## Success Criteria

✅ Requirements gathering works end-to-end
✅ Plans generated from requirements are sensible
✅ Tools execute reliably with proper error handling
✅ User can see real-time progress in terminal
✅ Execution can be cancelled gracefully
✅ Failed steps are reflected and fixed automatically
✅ All executions tracked in database with full audit trail
✅ Cost per execution is calculated and stored
✅ System can handle 100+ step plans without degradation

