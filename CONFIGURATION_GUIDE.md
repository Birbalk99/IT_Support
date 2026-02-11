# ============================================
# SECURITY CONFIGURATION GUIDE
# ============================================

## JWT Authentication (Backend Security)
**SECRET_KEY**: Ye JWT token encryption ke liye hai, LLM ke liye NAHI!
- Minimum 32 characters hona chahiye
- Production mein isko strong random string se replace karo
- `openssl rand -hex 32` se generate kar sakte ho

## Rate Limiting Control
Agar API hit limit disable karna ho:
```env
RATE_LIMIT_ENABLED=False
```

## User ID Validation Control
Agar user ID validation hatana ho:
```env
ENABLE_USER_ID_VALIDATION=False
```

## URL Whitelist Control  
Agar URL restriction hatana ho:
```env
ENABLE_URL_WHITELIST=False
```

# ============================================
# LLM CONFIGURATION GUIDE
# ============================================

## Provider Selection
Choose karo kaunsa LLM use karna hai:
- openai: OpenAI GPT models
- azure_openai: Azure hosted OpenAI
- anthropic: Claude models
- google: Google Gemini
- local: Ollama ya local LLM

## Setup Examples:

### For OpenAI:
```env
LLM_PROVIDER="openai"
OPENAI_API_KEY="sk-your-api-key-here"
OPENAI_MODEL="gpt-4"
```

### For Azure OpenAI:
```env
LLM_PROVIDER="azure_openai"
AZURE_OPENAI_API_KEY="your-azure-key"
AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
AZURE_OPENAI_DEPLOYMENT_NAME="your-deployment"
```

### For Anthropic Claude:
```env
LLM_PROVIDER="anthropic"
ANTHROPIC_API_KEY="your-anthropic-key"
ANTHROPIC_MODEL="claude-3-sonnet-20240229"
```

### For Local LLM (Ollama):
```env
LLM_PROVIDER="local"
LOCAL_LLM_URL="http://localhost:11434"
LOCAL_LLM_MODEL="llama2"
```

## LLM Features Control
```env
LLM_ENABLE_TICKET_ANALYSIS=True      # Ticket auto-categorization
LLM_ENABLE_AUTO_RESPONSE=True        # Auto-suggest solutions
LLM_ENABLE_SENTIMENT_ANALYSIS=True   # Analyze user sentiment
```

# ============================================
# SCALABILITY TIPS
# ============================================

1. **Disable Features Easily**: Har feature ko True/False se control karo
2. **Switch LLM Provider**: Sirf LLM_PROVIDER change karo, code nahi
3. **Rate Limiting**: Redis add karo for distributed rate limiting
4. **Database**: SQLite se PostgreSQL/MySQL mein migrate karo production ke liye

# ============================================
# QUICK DISABLE GUIDE
# ============================================

Security hatana ho to:
```env
ENABLE_USER_ID_VALIDATION=False
ENABLE_URL_WHITELIST=False  
RATE_LIMIT_ENABLED=False
```

LLM disable karna ho to:
```env
LLM_ENABLE_TICKET_ANALYSIS=False
LLM_ENABLE_AUTO_RESPONSE=False
LLM_ENABLE_SENTIMENT_ANALYSIS=False
```
