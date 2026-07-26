                POST /chat
                     │
                     ▼
              RuntimeService
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
ConversationService MessageService LLMService
                                      │
                                      ▼
                                 OpenAI/OpenRouter/...