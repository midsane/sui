# Implementation Roadmap: Execution System

## Executive Summary

Your system is at a critical juncture. The intent router works well, but the execution pipeline is incomplete. This roadmap outlines a **phased approach** to build a production-ready execution system that can:

1. ✅ Gather task requirements interactively
2. ✅ Generate step-by-step plans
3. ✅ Execute tools reliably with error recovery
4. ✅ Provide real-time feedback in terminal
5. ✅ Track all executions in database
6. ✅ Allow user cancellation at any time

**Timeline**: 2-3 weeks for MVP (Phase 1-3)

---

## Phase 1: Foundation (Week 1)

### 1.1 Fix LLM Service - Structured Output Support
**Goal**: Enable RequirementAgent and others to get JSON responses

**Files to modify**:
- `app/llms/schemas.py`: Make `ChatResult` generic
- `app/llms/providers/base.py`: Add `structured_llm_call()` method
- `app/llms/providers/gemini.py`: Implement structured output
- `app/llms/service.py`: Add `response_model` parameter

**Complexity**: Low  
**Time**: 2-3 hours

**Deliverable**: 
```python
result = await llm_service.llm_call(
    messages=history,
    response_model=RequirementResponse
)
```

---

### 1.2 Create Tool Abstraction Layer
**Goal**: Build foundation for tool execution

**New files**:
- `app/execution/tools/base.py`: `IToolProvider` interface
- `app/execution/tools/registry.py`: `ToolRegistry` class
- `app/execution/tools/schemas.py`: Tool I/O types
- `app/execution/tools/context.py`: `ExecutionContext`

**Files to modify**:
- Create `app/execution/tools/__init__.py`

**Complexity**: Medium  
**Time**: 4-5 hours

**Deliverable**:
```python
registry = ToolRegistry(user_permissions)
tool = registry.get_tool("file_read")
output = await tool.execute({"path": "/file.txt"})
```

---

### 1.3 Implement Core Tools (File, Bash)
**Goal**: Basic file and command execution

**New files**:
- `app/execution/tools/file_tool.py`: Read/write/list files
- `app/execution/tools/bash_tool.py`: Execute shell commands
- `app/execution/tools/http_tool.py`: HTTP requests (basic)

**Complexity**: Medium  
**Time**: 5-6 hours

**Deliverable**:
- FileTool: read, write, list operations
- BashTool: execute with timeout and output capture
- HttpTool: GET/POST (GET priority)

---

### 1.4 Create Execution Session Management
**Goal**: Track execution state and data

**New files**:
- `app/entities/execution_sessions/models.py`: `ExecutionSession` model
- `app/entities/execution_sessions/schemas.py`: Dataclass schemas
- `app/entities/execution_sessions/repository.py`: Database access
- `app/entities/execution_sessions/service.py`: Business logic

**Files to modify**:
- Create migration for `execution_sessions` table

**Complexity**: Medium  
**Time**: 4-5 hours

**Deliverable**:
```python
session = await session_service.create(
    task="Build a website",
    user_id=user_id
)
# Track session state throughout execution
await session_service.update(session)
```

---

## Phase 2: Pipeline Components (Week 2)

### 2.1 Implement Requirement Gatherer
**Goal**: Ask user questions until task is clear

**New files**:
- `app/execution/requirements/agent.py`: Complete implementation
- `app/execution/requirements/prompts.py`: Improve prompts

**Files to modify**:
- `app/execution/requirements/schemas.py`: Add more fields if needed

**Complexity**: Medium  
**Time**: 3-4 hours

**Deliverable**:
```python
gatherer = RequirementGatherer(llm_service)
requirement = await gatherer.gather(history)
# requirement.status: COMPLETE or NEEDS_INPUT
# requirement.question: Next question to ask (if needed)
# requirement.summary: Task summary (if complete)
```

---

### 2.2 Implement Execution Planner
**Goal**: Convert requirements into step-by-step plan

**New files**:
- `app/execution/planning/planner.py`: Complete implementation
- `app/execution/planning/prompts.py`: Planning prompts

**Files to modify**:
- `app/execution/planning/schemas.py`: Ensure ToolCall schema exists

**Complexity**: Medium  
**Time**: 4-5 hours

**Deliverable**:
```python
planner = ExecutionPlanner(llm_service)
plan = await planner.plan(
    requirements=requirement.summary,
    tools_available=registry.list_available()
)
# plan.goal: Description of goal
# plan.steps: List[PlanStep] with descriptions and tool_calls
```

---

### 2.3 Create Step Executor
**Goal**: Execute individual steps and handle tool calls

**New files**:
- `app/execution/executor/step_runner.py`: Single step execution
- `app/execution/executor/tool_parser.py`: Parse tool calls from LLM
- `app/execution/executor/output_store.py`: Store step outputs

**Files to modify**:
- `app/execution/executor/executor.py`: Integrate components
- `app/execution/executor/context.py`: Already exists, maybe enhance

**Complexity**: High  
**Time**: 6-7 hours

**Deliverable**:
```python
executor = StepExecutor(tool_registry, llm_service)
async for update in executor.execute_step(session, plan.steps[0]):
    yield update  # Stream to terminal
    # Updates include: tool_name, tool_output, status
```

---

### 2.4 Implement Evaluator
**Goal**: Check if steps succeeded

**New files**:
- `app/execution/evaluation/evaluator.py`: Complete implementation
- `app/execution/evaluation/prompts.py`: Evaluation prompts

**Files to modify**:
- `app/execution/evaluation/schemas.py`: Add fields if needed

**Complexity**: Low-Medium  
**Time**: 2-3 hours

**Deliverable**:
```python
evaluator = Evaluator(llm_service)
result = await evaluator.evaluate(
    step=plan.steps[0],
    outputs=step_outputs,
    context=session
)
# result.success: bool
# result.confidence: float (0.0-1.0)
# result.error_message: str if failed
```

---

## Phase 3: Integration (Week 2-3)

### 3.1 Implement Reflector (Error Recovery)
**Goal**: Fix failed steps automatically

**New files**:
- `app/execution/reflection/reflector.py`: Complete implementation
- `app/execution/reflection/prompts.py`: Reflection prompts

**Files to modify**:
- `app/execution/reflection/schemas.py`: Ensure has fix_strategy

**Complexity**: Medium  
**Time**: 3-4 hours

**Deliverable**:
```python
reflector = Reflector(llm_service)
fix = await reflector.reflect(
    original_step=plan.steps[0],
    outputs=step_outputs,
    error_analysis=evaluator_result
)
# fix.corrected_step: Modified PlanStep to retry
# fix.retry_strategy: How to approach retry
```

---

### 3.2 Create Execution State Manager
**Goal**: Manage state transitions safely

**New files**:
- `app/execution/state_manager.py`: State machine logic

**Complexity**: Medium  
**Time**: 3-4 hours

**Deliverable**:
```python
state_mgr = ExecutionStateManager()
await state_mgr.transition(
    session,
    from_status=GATHERING_REQUIREMENTS,
    to_status=PLANNING
)
# Validates transition is allowed
# Updates database
```

---

### 3.3 Build Main Execution Pipeline
**Goal**: Orchestrate entire flow

**Files to modify**:
- `app/execution/service.py`: Complete the ExecutionService
- `app/execution/__init__.py`: Export all components

**New files**:
- `app/execution/pipeline.py`: Orchestration logic

**Complexity**: High  
**Time**: 6-8 hours

**Deliverable**:
```python
pipeline = ExecutionPipeline(
    session_service=session_service,
    requirement_gatherer=req_gatherer,
    planner=planner,
    step_executor=executor,
    evaluator=evaluator,
    reflector=reflector,
)

async for update in pipeline.execute_session(task, user_id):
    # Stream to terminal
    # update.status, message, step_index, etc.
    yield update.format_for_terminal()
```

---

### 3.4 Integrate with Runtime Service
**Goal**: Wire pipeline into chat flow

**Files to modify**:
- `app/runtime/service.py`: Update stream_chat() for EXECUTE intent
- `app/terminal/main.py`: Pass new components to ExecutionService

**Complexity**: Low  
**Time**: 2-3 hours

**Deliverable**:
```python
# User types: "Build a FastAPI project"
# Intent: EXECUTE
async for chunk in runtime.stream_chat(prompt):
    yield chunk  # Real-time feedback to terminal
```

---

## Phase 4: Polish (Week 3)

### 4.1 Terminal UI Enhancement
**Goal**: Better feedback display

**Files to modify**:
- `app/terminal/renderer.py`: Add execution rendering
- `app/terminal/main.py`: Better status display

**Complexity**: Low  
**Time**: 2-3 hours

---

### 4.2 Error Messages & Recovery UI
**Goal**: User can help with failures

**Files to modify**:
- `app/terminal/commands.py`: Add execution commands
- Interactive prompts for user intervention

**Complexity**: Medium  
**Time**: 3-4 hours

---

### 4.3 Comprehensive Testing
**Goal**: Test all components

**Files to create**:
- `tests/execution/test_*.py`: Unit tests for each component
- `tests/integration/test_pipeline.py`: End-to-end test

**Complexity**: High  
**Time**: 8-10 hours

---

## File Structure After Implementation

```
app/
├── execution/
│   ├── __init__.py
│   ├── service.py (rewrite)
│   ├── schemas.py ✓ (exists)
│   ├── session.py ✓ (exists)
│   ├── state_manager.py (NEW)
│   ├── pipeline.py (NEW)
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py (NEW)
│   │   ├── registry.py (NEW)
│   │   ├── schemas.py (NEW)
│   │   ├── context.py (NEW)
│   │   ├── file_tool.py (NEW)
│   │   ├── bash_tool.py (NEW)
│   │   └── http_tool.py (NEW)
│   ├── requirements/
│   │   ├── agent.py (enhance)
│   │   ├── prompts.py ✓ (exists)
│   │   └── schemas.py ✓ (exists)
│   ├── planning/
│   │   ├── planner.py (NEW)
│   │   ├── prompts.py (NEW)
│   │   └── schemas.py (NEW)
│   ├── executor/
│   │   ├── executor.py (enhance)
│   │   ├── step_runner.py (NEW)
│   │   ├── tool_parser.py (NEW)
│   │   ├── output_store.py (NEW)
│   │   ├── context.py ✓ (exists)
│   │   └── __init__.py
│   ├── evaluation/
│   │   ├── evaluator.py (NEW)
│   │   ├── prompts.py (NEW)
│   │   └── schemas.py (NEW)
│   └── reflection/
│       ├── reflector.py (NEW)
│       ├── prompts.py ✓ (exists)
│       └── schemas.py (NEW)
├── entities/
│   ├── execution_sessions/
│   │   ├── __init__.py
│   │   ├── models.py (NEW)
│   │   ├── schemas.py (NEW)
│   │   ├── repository.py (NEW)
│   │   └── service.py (NEW)
│   └── execution/
│       ├── __init__.py
│       ├── models.py ✓ (exists)
│       ├── schemas.py ✓ (exists)
│       ├── repository.py (NEW)
│       └── service.py (NEW)
├── llms/
│   └── (update for structured output)
└── runtime/
    └── service.py (update integration)
```

---

## Database Migrations Needed

1. **execution_sessions** table
   - Fields: id, user_id, task, requirements, plan, status, etc.
   
2. **step_outputs** table
   - Track each step execution and result

3. **tool_usage** table
   - Monitor tool usage and costs

---

## Testing Pyramid

```
                    E2E Tests (1 test)
                   Integration Tests (5 tests)
               Component Tests (15 tests)
           Unit Tests (30+ tests)
```

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| LLM structured output fails | Medium | High | Fallback to text parsing + retry |
| Tool execution hangs | Medium | High | Timeouts + cancellation handling |
| State corruption | Low | Critical | Database transactions + validation |
| User input loop forever | Low | Medium | Max iterations + user abort |

---

## Success Metrics

- [ ] Execute "Create a TODO app with FastAPI" end-to-end
- [ ] All steps show real-time in terminal
- [ ] Can cancel mid-execution gracefully
- [ ] Failed step auto-fixed by reflector
- [ ] All executions saved to database
- [ ] 90%+ test coverage on critical paths

---

## Dependencies to Add

```toml
[dependencies]
pydantic>=2.0.0  # For structured output validation
python-dotenv>=1.0.0  # For env management in tools
rich>=15.0.0  # Already exists, good for UI
```

---

## Next Steps

1. **Review** this roadmap with team
2. **Decide** on tool set (file, bash, http for Phase 1?)
3. **Start Phase 1**: LLM structured output is foundation
4. **Track progress** against timeline
5. **Adjust** if needed

