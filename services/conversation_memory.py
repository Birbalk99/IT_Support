"""
Conversation Memory Service
Stores conversation history per session for context continuity
"""
from typing import Dict, List
from datetime import datetime, timedelta
from core.logging.logger import agent_logger


class ConversationMemory:
    """In-memory conversation storage with auto-cleanup"""
    
    def __init__(self, max_age_minutes: int = 30):
        """
        Initialize conversation memory
        
        Args:
            max_age_minutes: Auto-delete conversations older than this
        """
        self._conversations: Dict[str, Dict] = {}
        self.max_age_minutes = max_age_minutes
        
        agent_logger.info(
            f"Conversation memory initialized (max age: {max_age_minutes}min)",
            method="INIT"
        )
    
    def add_message(self, session_id: str, role: str, content: str):
        """
        Add a message to conversation history
        
        Args:
            session_id: User's session ID
            role: "user" or "assistant"
            content: Message content
        """
        if session_id not in self._conversations:
            self._conversations[session_id] = {
                "messages": [],
                "created_at": datetime.utcnow(),
                "last_updated": datetime.utcnow()
            }
        
        self._conversations[session_id]["messages"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        self._conversations[session_id]["last_updated"] = datetime.utcnow()
        
        agent_logger.info(
            f"Message added to session {session_id[:8]}...",
            method="ADD_MESSAGE",
            extra_info={
                "role": role,
                "total_messages": len(self._conversations[session_id]["messages"])
            }
        )
    
    def get_history(self, session_id: str, max_messages: int = 20) -> List[Dict]:
        """
        Get conversation history for a session
        
        Args:
            session_id: User's session ID
            max_messages: Maximum number of recent messages to return
            
        Returns:
            List of message dicts with role and content
        """
        if session_id not in self._conversations:
            agent_logger.info(
                f"No history found for session {session_id[:8]}...",
                method="GET_HISTORY"
            )
            return []
        
        messages = self._conversations[session_id]["messages"]
        # Return last N messages
        history = messages[-max_messages:] if len(messages) > max_messages else messages
        
        agent_logger.info(
            f"Retrieved {len(history)} messages for session {session_id[:8]}...",
            method="GET_HISTORY"
        )
        
        return history
    
    def clear_session(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self._conversations:
            del self._conversations[session_id]
            agent_logger.info(
                f"Session {session_id[:8]}... cleared",
                method="CLEAR_SESSION"
            )
    
    def cleanup_old_conversations(self):
        """Remove conversations older than max_age_minutes"""
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.max_age_minutes)
        
        old_sessions = [
            session_id
            for session_id, data in self._conversations.items()
            if data["last_updated"] < cutoff_time
        ]
        
        for session_id in old_sessions:
            del self._conversations[session_id]
        
        if old_sessions:
            agent_logger.info(
                f"Cleaned up {len(old_sessions)} old conversations",
                method="CLEANUP"
            )
    
    def get_session_count(self) -> int:
        """Get total active sessions"""
        return len(self._conversations)


# Global instance
conversation_memory = ConversationMemory(max_age_minutes=30)
