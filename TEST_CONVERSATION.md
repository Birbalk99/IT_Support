# Test Conversation Memory

## Test with curl/Postman

### First Message (No History)
```bash
POST http://localhost:8000/api/llm/query

{
  "query": "Hi, I have issue with my laptop charger",
  "conversation_history": []
}
```

### Second Message (With History)
```bash
POST http://localhost:8000/api/llm/query

{
  "query": "Yes, it's company issued laptop charger. Adapter is working but power cable is not working",
  "conversation_history": [
    {
      "role": "user",
      "content": "Hi, I have issue with my laptop charger"
    },
    {
      "role": "assistant",
      "content": "**Charger Issue Noted**\n\n1. Is this a company-issued laptop charger?\n2. Is the adapter light on but cable not charging?\n\nNeed more details?"
    }
  ]
}
```

### Third Message (Extended History)
```bash
POST http://localhost:8000/api/llm/query

{
  "query": "I tested with another cable, same issue",
  "conversation_history": [
    {
      "role": "user",
      "content": "Hi, I have issue with my laptop charger"
    },
    {
      "role": "assistant",
      "content": "**Charger Issue Noted**\n\n1. Is this a company-issued laptop charger?\n2. Is the adapter light on but cable not charging?\n\nNeed more details?"
    },
    {
      "role": "user",
      "content": "Yes, it's company issued laptop charger. Adapter is working but power cable is not working"
    },
    {
      "role": "assistant",
      "content": "**Power Cable Issue**\n\n1. Check cable for visible damage\n2. Test with another power cable\n\nTried these steps?"
    }
  ]
}
```

## Expected Behavior
- Agent should maintain context across all messages
- NO repeated greetings after first message
- Should continue same topic (charger issue)
- Should remember previous answers (company laptop, adapter works)

## Frontend Must Send
```javascript
const conversationHistory = [
  { role: "user", content: "previous user message" },
  { role: "assistant", content: "previous bot response" },
  // ... all previous messages
];

fetch('http://localhost:8000/api/llm/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: currentUserMessage,
    conversation_history: conversationHistory
  })
});
```
