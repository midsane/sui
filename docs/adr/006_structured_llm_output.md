# ADR-006: Structured LLM Output Support

**Date**: 2026-07-29  
**Status**: Proposed  
**Impact**: Medium

## Problem

The current `LLMService` only returns text responses. But the execution pipeline needs structured data:

1. **RequirementGatherer** needs: status, question, summary, reasoning (JSON)
2. **ExecutionPlanner** needs: goal, steps array with descriptions (JSON)
3. **Evaluator** needs: success boolean, confidence score, error details (JSON)
4. **Reflector** needs: corrected step, explanation, retry strategy (JSON)

Currently `RequirementAgent` calls:
```python
result = await self.llm_service.llm_call(
    messages=history,
    system_prompt=REQUIREMENT_PROMPT,
    response_schema=RequirementResponse,  # ← This doesn't exist!
)
```

This will fail at runtime. We need proper structured output support.

## Solution

### Extend LLMService with Structured Output

```python
class LLMService:
    async def llm_call(
        self,
        messages: list[Message],
        system_prompt: str | None = None,
        response_model: type[T] | None = None,  # ← NEW
    ) -> ChatResult[T]:
        """
        Call LLM and optionally parse response into structured type
        
        response_model can be:
        - Pydantic BaseModel
        - Dataclass
        - TypedDict
        - Simple Python type (str, int, bool)
        """
        
        if response_model is None:
            # Existing behavior: return text
            return await self._provider().llm_call(history)
        
        # New behavior: structured output
        return await self._provider().structured_llm_call(
            history=history,
            response_model=response_model,
        )
```

### Provider Interface Update

Each provider (Gemini, OpenAI, etc.) implements:

```python
class BaseProvider(ABC):
    async def llm_call(
        self, messages: list[Message]
    ) -> ChatResult[str]:
        """Existing text-only API"""
    
    async def structured_llm_call(
        self, messages: list[Message], response_model: type[T]
    ) -> ChatResult[T]:
        """NEW: Structured output"""
        # Provider-specific implementation:
        # - Gemini uses json_schema parameter
        # - OpenAI uses JSON mode + format hints
        # - OpenRouter uses provider-native support
```

### Implementation per Provider

#### Gemini (Already supports JSON schema)
```python
# In GeminiProvider.structured_llm_call():
schema = json_schema_from_model(response_model)
response = await client.aio.generate_content(
    messages=formatted_messages,
    generation_config={"response_mime_type": "application/json"}
)
return parse_obj_as(response_model, json.loads(response.text))
```

#### OpenAI (Using JSON mode)
```python
# In OpenAIProvider.structured_llm_call():
# Format prompt to ask for JSON
messages_with_format = self._add_json_format_instructions(
    messages, response_model
)
response = await client.chat.completions.create(
    messages=messages_with_format,
    response_format={"type": "json_object"},
)
return parse_obj_as(response_model, json.loads(response.content))
```

### Usage in Components

**Before (broken):**
```python
class RequirementAgent:
    async def gather(self, history):
        result = await self.llm_service.llm_call(
            messages=history,
            response_schema=RequirementResponse,  # ✗ Doesn't work
        )
```

**After (works):**
```python
class RequirementAgent:
    async def gather(self, history):
        result = await self.llm_service.llm_call(
            messages=history,
            system_prompt=REQUIREMENT_PROMPT,
            response_model=RequirementResponse,  # ✓ Works!
        )
        # result.data is RequirementResponse instance
        return result.data
```

### Schema Definitions

Define schemas as dataclasses (simpler than Pydantic):

```python
# requirements/schemas.py
@dataclass
class RequirementResponse:
    status: RequirementStatus  # "complete" or "needs_input"
    reasoning: str
    question: str | None = None
    summary: str | None = None

# planning/schemas.py
@dataclass
class PlanStep:
    index: int
    description: str
    tool_calls: list[ToolCall]  # What tools to use

@dataclass
class ExecutionPlan:
    goal: str
    steps: list[PlanStep]
    estimated_cost: float  # Approximate LLM call cost

# evaluation/schemas.py
@dataclass
class EvaluationResult:
    success: bool
    confidence: float  # 0.0 to 1.0
    evidence: str  # Why we think it succeeded
    error_message: str | None = None

# reflection/schemas.py
@dataclass
class ReflectionResult:
    analysis: str
    corrected_step: PlanStep
    retry_strategy: str
    max_retries_recommended: int
```

### Error Handling

If LLM doesn't return valid JSON:

```python
class StructuredOutputError(Exception):
    """Raised when LLM output doesn't match schema"""
    
    def __init__(
        self,
        response_model: type,
        raw_output: str,
        validation_error: Exception,
    ):
        self.response_model = response_model
        self.raw_output = raw_output
        self.validation_error = validation_error
```

Retry logic:

```python
async def call_with_retry(
    llm_service,
    messages,
    response_model,
    max_retries=3,
):
    for attempt in range(max_retries):
        try:
            return await llm_service.llm_call(
                messages=messages,
                response_model=response_model,
            )
        except StructuredOutputError as e:
            if attempt == max_retries - 1:
                raise
            # Retry with more explicit format hint
            messages.append(Message(
                role=MessageRole.USER,
                content=f"Previous response invalid. Return valid JSON matching {response_model}."
            ))
```

## Tradeoffs

### Pros
✅ Type-safe structured outputs  
✅ Validation happens in LLMService  
✅ Easy to extend with new schemas  
✅ Prompts clearly specify format  
✅ Composable with existing services  

### Cons
❌ Adds provider-specific code  
❌ LLM might not follow format perfectly  
❌ Retry logic increases latency  
❌ Need JSON schema for each component  

## Implementation Plan

1. **Update ChatResult** to be generic: `ChatResult[T]`
2. **Add structured_llm_call()** to BaseProvider
3. **Implement in GeminiProvider** (simplest)
4. **Implement in OpenAIProvider** (JSON mode)
5. **Update RequirementAgent** to use new API
6. **Add to all pipeline components** (Planner, Evaluator, Reflector)
7. **Retry logic** for validation failures
8. **Comprehensive tests** for each schema

## Testing Strategy

- Test each provider's structured output separately
- Mock LLM to return invalid JSON, verify retry
- Test schema validation with edge cases
- Verify output matches schema types
- Performance test (latency of structured calls)

## Alternatives Considered

### 1. Use Pydantic with TypeAdapter
**Why rejected**: Overkill for simple schemas, dataclasses are lighter.

### 2. Parse text output with regex
**Why rejected**: Brittle, error-prone, not reliable.

### 3. Only OpenAI with JSON mode
**Why rejected**: Want to support multiple providers (Gemini already works).

### 4. Hardcode expected outputs
**Why rejected**: No type checking, prone to errors.

## Future Evolution

- **Schema Versioning**: Track schema changes over time
- **Output Validation**: Stricter validation of LLM outputs
- **Caching**: Cache frequent structured calls
- **Batch Processing**: Structured outputs for multiple queries
- **Fallback Strategies**: Use simpler schemas if complex fails
