User
  │
  ▼
Chat API
  │
  ▼
Orchestrator
  │
  ├── Normal chat
  │      └── Answer immediately
  │
  └── Coding task
         │
         ▼
    Create Execution
         │
         ▼
    Agent Loop
      ├── Think
      ├── Use tools
      ├── Modify files
      ├── Run commands
      └── Finish

Workspace
├── project/
└── .sui/


POST /chat

↓

Runtime

↓

if normal question:
    return LLM response

if coding request:
    execution = create_execution()

    while not done:
        think
        call tool
        update execution
        repeat

↓

Return result


Entities:

Agent
Execution
Model
Messages

Tool system:

read_file()
write_file()
list_files()
grep()
bash()
git()
web_search()