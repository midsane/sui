# ADR-005: Execution Pipeline and State Management

**Date**: 2026-07-29  
**Status**: Proposed  
**Impact**: High

## Problem

Currently, when Intent=EXECUTE, there's no orchestration of the execution flow. We need:
1. **Clear State Machine**: Track progress through gathering → planning → execution
2. **User Involvement**: Ask questions, show plan, get approval before execution
3. **Real-time Feedback**: Stream progress to terminal as steps complete
4. **Error Recovery**: Auto-fix failures or ask user for help
5. **Cancellation**: User can stop execution at any point
6. **Persistence**: Track all execution details in database

## Solution

### Execution Session Lifecycle

```
User says "Build a website"
    ↓
Create ExecutionSession
    status = GATHERING_REQUIREMENTS
    ↓
Loop: RequirementGatherer
    ├─ Ask for missing info (1 question at a time)
    ├─ User answers
    ├─ Update requirements
    └─ All required? → status = PLANNING
    ↓
ExecutionPlanner creates plan
    status = PLANNING
    ↓
Show plan to user
    status = AWAITING_APPROVAL
    ↓
User approves → status = EXECUTING
    ↓
For each step in plan:
    ├─ status = STEP_EXECUTING
    ├─ Call tool
    ├─ status = STEP_EVALUATING
    ├─ Check success
    ├─ Step succeeded?
    │  ├─ Yes: continue to next step
    │  └─ No: status = REFLECTING
    │         Reflector generates fix
    │         Try step again (max 2 retries)
    │
    └─ Still failed?
       └─ Ask user: skip, retry, or abort?
    ↓
status = COMPLETED (or FAILED)
```

### Core Components

#### 1. ExecutionSession

```python
@dataclass
class ExecutionSession:
    id: UUID
    user_id: UUID
    task: str
    
    # Requirements phase
    requirements: dict[str, Any]
    requirements_status: RequirementStatus  # INCOMPLETE | COMPLETE
    
    # Planning phase
    plan: ExecutionPlan | None
    plan_approved: bool = False
    
    # Execution phase
    current_step_index: int = 0
    step_outputs: list[StepOutput] = field(default_factory=list)
    status: ExecutionStatus
    
    # Metadata
    started_at: datetime
    updated_at: datetime
    finished_at: datetime | None
    
    # Cancellation
    cancelled_at: datetime | None
    cancellation_reason: str | None
```

#### 2. ExecutionStateManager

Controls state transitions and ensures consistency:

```python
class ExecutionStateManager:
    async def transition(
        self,
        session: ExecutionSession,
        to_status: ExecutionStatus,
    ) -> None:
        """Validate and perform state transition"""
        # Validates: GATHERING_REQUIREMENTS → PLANNING only if complete
        # Validates: PLANNING → EXECUTING only if approved
        # etc.
    
    async def handle_interrupt(self, session: ExecutionSession) -> None:
        """Handle Ctrl+C gracefully"""
        # Move to CANCELLED, save state, cleanup
    
    async def rollback(
        self,
        session: ExecutionSession,
        to_step: int,
    ) -> None:
        """Rewind to specific step for retry"""
```

#### 3. Pipeline Orchestrator

```python
class ExecutionPipeline:
    async def execute_session(
        self,
        task: str,
        user_id: UUID,
    ) -> AsyncIterator[ExecutionUpdate]:
        """Run complete session with streaming updates"""
        
        session = ExecutionSession(task=task, user_id=user_id)
        
        # Phase 1: Gather requirements
        async for update in self._gather_requirements(session):
            yield update
        
        # Phase 2: Plan
        async for update in self._plan(session):
            yield update
        
        # Phase 3: Get approval
        session.plan_approved = await self._get_approval(session)
        if not session.plan_approved:
            yield ExecutionUpdate(status=FAILED, reason="User rejected plan")
            return
        
        # Phase 4: Execute steps
        async for update in self._execute_steps(session):
            yield update
            
            # Check for cancellation
            if session.cancelled_at is not None:
                yield ExecutionUpdate(status=CANCELLED)
                break
        
        # Finalize
        await self._finalize(session)
        yield ExecutionUpdate(status=COMPLETED)
```

### Step Execution with Reflection

```python
class StepExecutor:
    async def execute_step(
        self,
        session: ExecutionSession,
        step: PlanStep,
        retry_count: int = 0,
    ) -> AsyncIterator[ExecutionUpdate]:
        """
        Execute a single step:
        1. Parse tool calls from step description
        2. Execute each tool
        3. Evaluate success
        4. Reflect if failed
        """
        
        # Parse step to extract tool calls
        tool_calls = await self._parse_step(step)
        
        outputs = []
        for tool_call in tool_calls:
            yield ExecutionUpdate(
                status=STEP_EXECUTING,
                message=f"Running: {tool_call.tool_name}"
            )
            
            try:
                output = await self._execute_tool(
                    session, tool_call
                )
                outputs.append(output)
            except ToolExecutionError as e:
                outputs.append(e)
        
        # Evaluate if step succeeded
        success = await self._evaluate_step(
            step=step,
            outputs=outputs,
            context=session
        )
        
        if not success and retry_count < MAX_RETRIES:
            yield ExecutionUpdate(
                status=REFLECTING,
                message="Step failed, generating fix..."
            )
            
            # Reflect and generate corrected step
            corrected_step = await self._reflect(
                step=step,
                outputs=outputs,
                error_analysis=error_analysis
            )
            
            # Retry with corrected step
            async for update in self.execute_step(
                session, corrected_step, retry_count + 1
            ):
                yield update
        
        elif not success:
            yield ExecutionUpdate(
                status=STEP_FAILED,
                step_index=session.current_step_index,
                message="Max retries exceeded"
            )
```

### Real-time Updates Stream

All components yield `ExecutionUpdate` objects:

```python
@dataclass
class ExecutionUpdate:
    # Phase updates
    status: ExecutionStatus
    message: str | None = None
    
    # Requirement gathering
    question: str | None = None
    
    # Planning
    plan: ExecutionPlan | None = None
    
    # Execution
    step_index: int | None = None
    step_description: str | None = None
    tool_name: str | None = None
    tool_output: str | None = None
    
    # Errors
    error: str | None = None
    error_recovery: str | None = None
    
    # Progress
    progress: float | None = None  # 0.0 to 1.0
```

### Database Persistence

All sessions saved to `execution_sessions` table:

```python
class ExecutionSessionRepository:
    async def create(self, session: ExecutionSession) -> ExecutionSession:
        """Save new session"""
    
    async def update(self, session: ExecutionSession) -> None:
        """Update session state"""
    
    async def get_by_id(self, session_id: UUID) -> ExecutionSession:
        """Resume interrupted execution"""
    
    async def list_user_sessions(self, user_id: UUID) -> list[ExecutionSession]:
        """Show user all their executions"""
```

## Key Design Decisions

### 1. **Linear Execution Only (Phase 1)**
- Steps execute one at a time in order
- Easier to implement, understand, and debug
- Foundation for parallel execution later
- Decision: Keep it simple initially

### 2. **Async Streaming All Updates**
- Terminal gets real-time feedback
- No waiting for step to complete before showing progress
- Easy to add UI updates later
- Cost: Slightly more complex event management

### 3. **Automatic Retry with Reflection**
- Failed steps auto-retry with LLM-generated fix
- Limited to 2 retries to avoid infinite loops
- User can manually override
- Cost: Extra LLM calls (but catches real errors)

### 4. **Approval Gate Before Execution**
- Show plan to user, get explicit approval
- Prevents accidental execution
- User can modify plan before approval
- Cost: One extra interaction point

### 5. **Graceful Cancellation**
- Ctrl+C stops execution without data loss
- Session saved so can resume later
- Current step completes before cancelling
- Cost: Need careful interrupt handling

## Tradeoffs

### Pros
✅ Clear state machine prevents invalid transitions  
✅ Real-time feedback keeps user informed  
✅ Cancellation works gracefully  
✅ Automatic recovery from failures  
✅ Full audit trail in database  
✅ Can resume interrupted executions  

### Cons
❌ Sequential execution slower than parallel  
❌ Reflection adds LLM call cost  
❌ More complex state management  
❌ Need robust approval UI  

## Implementation Roadmap

1. **ExecutionSession** model + repository
2. **ExecutionStateManager** with state machine
3. **ExecutionPipeline** orchestrator
4. **StepExecutor** basic (just LLM calls)
5. **Tool integration** (execute actual tools)
6. **Reflection** component for error recovery
7. **Database persistence**
8. **Terminal UI** for all updates

## Testing Strategy

- State machine correctness (valid transitions only)
- Step executor with mocked tools
- Reflection generates valid fixes
- Cancellation doesn't lose data
- Resume from checkpoint works
- Concurrent sessions don't interfere

## Future Evolution

- **Parallel Execution**: Multiple steps at once
- **Branching Paths**: If/else in plan
- **Nested Plans**: Steps containing sub-plans
- **Agent Checkpoints**: Resume from any step
- **Plan Optimization**: Reorder steps for efficiency
