from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

from core.logging.logger import api_logger, agent_logger
from services.groq_service import groq_service
from services.conversation_memory import conversation_memory
from core.llm_config import llm_settings

router = APIRouter()

class ConversationMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class LLMRequest(BaseModel):
    query: str
    conversation_history: Optional[List[ConversationMessage]] = []
    user_id: Optional[str] = None

class LLMResponse(BaseModel):
    user_id: str
    session_id: str
    query: str
    response: str
    model: str
    timestamp: str

class SimpleQueryRequest(BaseModel):
    query: str

class SimpleQueryResponse(BaseModel):
    query: str
    response: str
    model: str
    timestamp: str


def get_user_from_session(request: Request) -> dict:
    """
    Automatically detect user_id and session_id from request
    
    Priority:
    1. X-User-ID header
    2. user_id query parameter
    3. Session cookie/token
    4. Client IP as fallback
    """
    user_id = None
    session_id = None
    
    # 1. Check headers
    user_id = request.headers.get("X-User-ID")
    session_id = request.headers.get("X-Session-ID")
    
    # 2. Check query params
    if not user_id:
        user_id = request.query_params.get("user_id")
    if not session_id:
        session_id = request.query_params.get("session_id")
    
    # 3. Check request state (set by middleware)
    if not user_id and hasattr(request.state, "user_id"):
        user_id = request.state.user_id
    
    # 4. Generate session_id from client info if not found
    if not session_id:
        client_ip = request.state.client_ip if hasattr(request.state, "client_ip") else "unknown"
        session_id = f"session_{client_ip}_{datetime.utcnow().timestamp()}"
    
    # 5. Fallback to IP if no user_id
    if not user_id:
        user_id = f"user_{request.state.client_ip if hasattr(request.state, 'client_ip') else 'unknown'}"
    
    return {
        "user_id": user_id,
        "session_id": session_id,
        "client_ip": request.state.client_ip if hasattr(request.state, "client_ip") else "unknown"
    }


@router.post("/query", response_model=LLMResponse)
async def llm_query(request: Request, llm_request: LLMRequest):
    """Process IT Help Desk query using configured LLM"""
    user_info = get_user_from_session(request)
    
    # Use provided user_id if available, otherwise use detected one
    final_user_id = llm_request.user_id or user_info["user_id"]
    final_session_id = user_info["session_id"]
    
    api_logger.info(
        f"LLM query from user: {final_user_id}, session: {final_session_id}",
        method="POST",
        extra_info={
            "query": llm_request.query[:100],
            "client_ip": user_info["client_ip"],
            "history_length": len(llm_request.conversation_history) if llm_request.conversation_history else 0
        }
    )
    
    # Log conversation history for debugging
    if llm_request.conversation_history:
        agent_logger.info(
            f"Conversation history: {len(llm_request.conversation_history)} messages",
            method="HISTORY",
            extra_info={"user_id": final_user_id}
        )
    
    # Get conversation history from memory (backend-managed)
    stored_history = conversation_memory.get_history(final_session_id)
    
    # Use frontend-provided history if available, otherwise use stored
    conversation_history = llm_request.conversation_history if llm_request.conversation_history else stored_history
    
    agent_logger.info(
        f"Using conversation history: {len(conversation_history)} messages (frontend: {len(llm_request.conversation_history) if llm_request.conversation_history else 0}, backend: {len(stored_history)})",
        method="MEMORY",
        extra_info={"session_id": final_session_id}
    )
    
    # Check if Groq service is available
    if llm_settings.LLM_PROVIDER == "groq":
        if not groq_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Groq service not configured. Please set GROQ_API_KEY in .env"
            )
        
        # Process query using Groq
        result = await groq_service.process_query(
            user_query=llm_request.query,
            user_id=final_user_id,
            conversation_history=conversation_history
        )
        
        # Store user message and bot response in memory
        conversation_memory.add_message(final_session_id, "user", llm_request.query)
        conversation_memory.add_message(final_session_id, "assistant", result["response"])
        
        # Cleanup old conversations periodically
        conversation_memory.cleanup_old_conversations()
        
        return LLMResponse(
            user_id=final_user_id,
            session_id=final_session_id,
            query=llm_request.query,
            response=result["response"],
            model=result["model"],
            timestamp=datetime.utcnow().isoformat()
        )
    
    # OpenAI or other providers
    else:
        # TODO: Implement OpenAI handler
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Provider {llm_settings.LLM_PROVIDER} not yet implemented"
        )


@router.post("/simple-query", response_model=SimpleQueryResponse)
async def simple_llm_query(request: SimpleQueryRequest):
    """
    Simple testing endpoint - only for normal queries without conversation history or user/session management
    No user_id or session_id needed from frontend
    """
    # Generate automatic session_id for testing
    test_session_id = f"test_session_{datetime.utcnow().timestamp()}"
    test_user_id = "test_user"
    
    api_logger.info(
        f"Simple query test: {request.query[:50]}...",
        method="POST",
        extra_info={"endpoint": "/simple-query"}
    )
    
    # Check if Groq service is available
    if llm_settings.LLM_PROVIDER == "groq":
        if not groq_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Groq service not configured. Please set GROQ_API_KEY in .env"
            )
        
        # Process query using Groq (no conversation history for testing)
        result = await groq_service.process_query(
            user_query=request.query,
            user_id=test_user_id,
            conversation_history=[]  # Fresh conversation for each test
        )
        
        agent_logger.info(
            "Simple query processed successfully",
            method="TEST",
            extra_info={"query_length": len(request.query)}
        )
        
        return SimpleQueryResponse(
            query=request.query,
            response=result["response"],
            model=result["model"],
            timestamp=datetime.utcnow().isoformat()
        )
    
    # OpenAI or other providers
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Provider {llm_settings.LLM_PROVIDER} not yet implemented"
        )
