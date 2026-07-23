Entities:

Agent
Task
Execution
Tool
Sandbox
Memory
LLM
Model
Evaluation
Reflection

                Agent
                  │
        ┌─────────┴─────────┐
        │                   │
      Model            ToolPermission
        │
        │
   Execution
        │
 ┌──────┼─────────────┐
 │      │             │
 │      │             │
Logs  ToolCalls    Memory
 │      │             │
 │      │             │
 └──────┼─────────────┘
        │
   Evaluation
        │
   Reflection

Database SQLAlchemy models:

Agent
Execution
Model
Tool
Memory
ExecutionLog

Plain python classes:

Planner
Loop Engine
Context Builder
Docker Executor
LLM Client
Reflection Engine
Memory Retriever


app/
├── agents/
│   ├── __init__.py
│   ├── models.py
│   ├── schemas.py
│   ├── repository.py
│   ├── service.py
│   ├── exceptions.py
│   └── api.py              # optional later
│
├── execution/
│   ├── __init__.py
│   ├── models.py
│   ├── schemas.py
│   ├── repository.py
│   ├── service.py
│   ├── exceptions.py
│   └── api.py
│
├── models/
│   ├── __init__.py
│   ├── models.py
│   ├── schemas.py
│   ├── repository.py
│   ├── service.py
│   └── providers.py
│
├── tools/
│   ├── __init__.py
│   ├── models.py
│   ├── schemas.py
│   ├── repository.py
│   ├── service.py
│   └── registry.py
│
├── memory/
│   ├── __init__.py
│   ├── models.py
│   ├── repository.py
│   ├── service.py
│   └── retriever.py
│
├── sandbox/
│   ├── __init__.py
│   ├── docker.py
│   ├── filesystem.py
│   └── executor.py
│
├── runtime/
│   ├── __init__.py
│   ├── planner.py
│   ├── loop.py
│   ├── executor.py
│   ├── context_builder.py
│   └── reflection.py
│
├── llm/
│   ├── __init__.py
│   ├── client.py
│   └── providers/
│       ├── __init__.py
│       ├── openai.py
│       ├── anthropic.py
│       ├── ollama.py
│       └── openrouter.py


    execution lifestyle
    User Request
      │
      ▼
Create Execution
      │
      ▼
Load Agent
      │
      ▼
Load Model
      │
      ▼
Build Context
      │
      ▼
Planner
      │
      ▼
Loop Engine
      │
      ▼
Tool Calls
      │
      ▼
Reflection
      │
      ▼
Evaluation
      │
      ▼
Complete Execution


This is the order I'd implement entities.

Phase 1 ✅
Agent

Done.

Phase 2
Model

Because agents need models.

Phase 3
Execution

Now agents can actually execute tasks.

Phase 4
Tool

Now executions can use tools.

Phase 5
ExecutionLog

Now we can observe what happened.

Phase 6
Memory

Now executions become stateful across runs.

Phase 7
Evaluation

Now we can score execution quality.

Phase 8
Reflection

Now the system can improve itself.


[ User Input ]
      │
      ▼
┌─────────────────────────┐
│ Orchestrator Router     │ ──(Simple Q&A)──► [ Simple LLM Stream ]
└─────────────────────────┘
      │ (Task detected)
      ▼
┌─────────────────────────┐
│ Planner Agent           │ ◄──► [ Memory / Chat History ]
│ (Defines Scope & Stack) │
└─────────────────────────┘
      │ (User Confirms Plan)
      ▼
┌─────────────────────────┐
│ Execution Agent (Loop)  │
│ - ReAct Loop            │
│ - Call MCP Tools        │ ──► [ Sandbox / Terminal ]
│ - Track Logs & Tokens   │
└─────────────────────────┘