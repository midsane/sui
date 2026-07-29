# ADR-004: Tool System Architecture (MCP-Inspired)

**Date**: 2026-07-29  
**Status**: Proposed  
**Impact**: High

## Problem

The current system has no abstraction for tools. When execution is triggered, there's no way to:
- Execute filesystem operations (read/write files)
- Run shell commands
- Make HTTP requests
- Search the web
- Discover what tools are available
- Check permissions before tool execution
- Handle tool errors gracefully
- Track tool usage/cost

This severely limits what the agent can accomplish. We need a pluggable, extensible tool system that's:
1. **Safe**: Permissions checked before execution
2. **Observable**: All tool calls logged and tracked
3. **Composable**: Tools can call other tools
4. **Extensible**: Easy to add new tools without modifying core
5. **Reliable**: Failures don't crash execution

## Solution

Implement a **tool provider interface** inspired by Model Context Protocol (MCP), with these principles:

### Architecture

```python
# Each tool is a Provider
class IToolProvider(ABC):
    name: str
    description: str
    schema: ToolSchema  # Input/output types
    
    async def execute(self, input: ToolInput) -> ToolOutput:
        """Execute the tool with given input"""
    
    requires_approval: bool  # Ask user before running?
    permission_level: PermissionLevel  # RESTRICTED | NORMAL | FULL

# Registry for discovery & execution
class ToolRegistry:
    def get_tool(self, name: str) -> IToolProvider:
        """Get tool by name, checking permissions"""
    
    def list_available(self) -> list[ToolInfo]:
        """All tools user has access to"""
    
    def execute(self, tool_name: str, input: dict) -> ToolOutput:
        """Execute tool with permission checks"""

# Execution context for tools to use
class ExecutionContext:
    session_id: UUID
    current_step: int
    tool_registry: ToolRegistry
    storage: ExecutionOutputStore
    user_id: UUID
```

### Built-in Tools (Phase 1)

1. **FileTool**
   - Operations: read, write, list, delete
   - Permissions: restricted to project directory
   - Use: Writing code files, reading configs

2. **BashTool**
   - Operations: execute commands with timeout
   - Permissions: restricted commands (can block `rm -rf`, etc.)
   - Use: Running builds, tests, installs

3. **HttpTool**
   - Operations: GET, POST, PUT, DELETE
   - Permissions: whitelist domains?
   - Use: Calling APIs

4. **WebSearchTool**
   - Operations: search, browse
   - Permissions: rate limited
   - Use: Finding latest info

5. **GitTool**
   - Operations: clone, commit, push, diff
   - Permissions: require user approval for push
   - Use: Version control

### Tool Execution Flow

```
LLM generates plan with tool calls
    ↓
StepExecutor picks a step
    ↓
Step contains: tool_name, tool_input
    ↓
ToolRegistry.execute(tool_name, tool_input)
    ├─ Check permissions
    ├─ Check approval required?
    │  └─ Yes: Ask user
    ├─ Validate input against schema
    ├─ Execute tool
    ├─ Capture output
    └─ Log to database
    ↓
Return output to LLM for next step
```

### Error Handling

- Tool execution timeout → Reflector suggests retry with timeout
- Permission denied → Skip step, ask user for approval
- Invalid input → Reflector generates corrected input
- Tool crashes → Caught, logged, reflected upon

### Cost Tracking

Each tool tracks:
- Number of calls
- Time taken
- Tokens used (if applicable)
- Cost (if applicable)
- Success/failure rate

Used for:
- Execution cost calculation
- Performance optimization suggestions
- Rate limiting

## Tradeoffs

### Pros
✅ Easy to add new tools without modifying core  
✅ Permissions/safety built-in  
✅ Observable (all tool calls logged)  
✅ Matches standard MCP design  
✅ Tools can be remoted/sandboxed later  

### Cons
❌ Initial overhead to define tool schemas  
❌ Tool execution latency if calling remote tools  
❌ Permission model needs careful design  
❌ Requires ongoing maintenance of tool APIs  

## Implementation Order

1. **IToolProvider** base class and ToolRegistry
2. **FileTool** (read, write, list)
3. **BashTool** (execute with whitelist)
4. **Integration** with StepExecutor
5. **Error handling** and reflection
6. **HttpTool** and **WebSearchTool** (Phase 2)

## Testing Strategy

- Unit tests for each tool in isolation
- Integration tests for ToolRegistry
- Permission model verification tests
- Error scenario testing (timeout, invalid input, etc.)
- Cost calculation accuracy tests

## Alternatives Considered

### 1. Hardcoded Tool Functions
**Why rejected**: Not extensible, makes core system complex, hard to add tools later.

### 2. Tool LLM Calling
**Why rejected**: Adds latency, LLM can make mistakes, no schema validation.

### 3. Only LLM-Generated Tool Calls
**Why rejected**: No control over what tools are called, security nightmare.

## Future Evolution

- **Tool Chaining**: Tools calling other tools automatically
- **Tool Learning**: Store successful tool call patterns
- **Remote Tools**: Execute tools on distributed workers
- **Tool Mocking**: Mock tools for testing
- **Tool Scoring**: Rate tools by success rate and efficiency
