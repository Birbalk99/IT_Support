"""
Groq AI Service
IT Help Desk classification and response generation using Groq
"""
from typing import Dict, Any, List
from groq import Groq

from core.llm_config import llm_settings
from core.logging.logger import agent_logger


class GroqService:
    """Groq AI service for IT Help Desk"""
    
    def __init__(self):
        """Initialize Groq client"""
        if not llm_settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not configured")
        
        self.client = Groq(api_key=llm_settings.GROQ_API_KEY)
        self.model = llm_settings.GROQ_MODEL
        self.temperature = llm_settings.GROQ_TEMPERATURE
        self.max_tokens = llm_settings.GROQ_MAX_TOKENS
        self.top_p = llm_settings.GROQ_TOP_P
        
        agent_logger.info(
            f"Groq service initialized with model: {self.model}",
            method="INIT"
        )
    
    async def process_query(
        self, 
        user_query: str, 
        user_id: str,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Process IT Help Desk query with conversation history
        
        Args:
            user_query: User's current question
            user_id: User identifier
            conversation_history: Previous conversation messages
            
        Returns:
            Dict with response and metadata
        """
        try:
            agent_logger.info(
                f"Processing query for user: {user_id}",
                method="PROCESS_QUERY",
                extra_info={"query_length": len(user_query)}
            )
            
            # Build system prompt
            system_prompt = self._build_system_prompt()
            
            # Build messages with conversation history
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if provided
            if conversation_history and len(conversation_history) > 0:
                agent_logger.info(
                    f"Adding {len(conversation_history)} messages to context",
                    method="PROCESS_QUERY"
                )
                for msg in conversation_history:
                    # Handle both dict and object format
                    if isinstance(msg, dict):
                        role = msg.get("role", "user")
                        content = msg.get("content", "")
                    else:
                        role = getattr(msg, "role", "user")
                        content = getattr(msg, "content", "")
                    
                    messages.append({
                        "role": role,
                        "content": content
                    })
            else:
                agent_logger.info(
                    "No conversation history provided - starting fresh",
                    method="PROCESS_QUERY"
                )
            
            # Add current user query
            messages.append({"role": "user", "content": user_query})
            
            # Call Groq API
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stream=False
            )
            
            response_text = completion.choices[0].message.content
            
            agent_logger.info(
                "Query processed successfully",
                method="PROCESS_QUERY",
                extra_info={
                    "user_id": user_id,
                    "response_length": len(response_text)
                }
            )
            
            return {
                "response": response_text,
                "model": self.model,
                "user_id": user_id,
                "status": "success"
            }
            
        except Exception as e:
            agent_logger.error(
                f"Groq API error: {str(e)}",
                method="PROCESS_QUERY",
                extra_info={"user_id": user_id}
            )
            
            # Return fallback response
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Please try again or contact IT support directly.",
                "model": self.model,
                "user_id": user_id,
                "status": "error",
                "error": str(e)
            }
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for IT Help Desk"""
        agent_name = llm_settings.AGENT_NAME
        return f"""You are {agent_name}, an AI-powered IT Help Desk assistant for a banking organization.

            CRITICAL RULES – FOLLOW STRICTLY:

            1. GREETING RULE (MOST IMPORTANT):
            - If conversation history is EMPTY or this is the FIRST message → Greet with "Hi! I'm {agent_name}"
            - If conversation history EXISTS → DO NOT greet again
            - NEVER say "Hi", "Hello", or "How can I assist you today?" in follow-up messages

            2. RESPONSE STYLE:
            - First message: Brief greeting + ONLY ONE diagnostic question
            - Follow-up messages:
            - First give ONE clear action to try
            - Then ask ONE confirmation or next diagnostic question
            - NO greetings in follow-ups
            - Keep responses SHORT (2–4 lines max)
            - Expand ONLY if user asks "explain more" or "give details"

            3. QUESTION ASKING (VERY STRICT):
            - Ask ONLY ONE question at a time
            - Ask questions ONLY when information is required
            - DO NOT ask multiple questions together
            - DO NOT repeat already answered questions
            - If enough information is available → provide solution directly

            4. ACTION BEFORE CONFIRMATION:
            - NEVER ask "Working now?" without giving an action first

            Correct pattern:
            - Please try [specific action].
            - Did [specific outcome] happen?

            Wrong pattern:
            - Working now?

            5. DIAGNOSTIC FLOW (MANDATORY):
            Always follow this order:
            1. Identify the issue category
            2. Ask ONE diagnostic question
            3. Suggest ONE action
            4. Confirm the result
            5. Proceed to next step OR escalate

            Do NOT jump directly to ticket creation.

            6. ISSUE-SPECIFIC BEHAVIOR:
            - Ask questions ONLY related to the identified issue
            - Example:
            - Charger issue → charger, cable, power socket
            - Network issue → WiFi, LAN, connectivity

            7. INFORMATION COLLECTION (ONLY IF ESCALATION IS NEEDED):
            - Collect details progressively, ONE BY ONE:
            - Issue type
            - Device or asset involved
            - Company-issued confirmation
            - Serial number (if applicable)

            - Never ask form-style multiple questions together

            8. DEPARTMENT CLASSIFICATION:
            - VPN & Remote Access: VPN, Citrix, remote desktop
            - Network: Internet, WiFi, LAN, speed issues
            - Desktop Support: OS, software, laptop/PC hardware
            - Asset Management: Charger, mouse, keyboard, monitor
            - Email: Outlook, email access, Teams
            - Security: Password reset, account locked
            - Server: Server down, database issues
            - Telephony: Desk phone, conference calls
            - Printer: Printing, scanning issues
            - Mobile: Company phones, tablets
            - Application: Business application errors

            9. CONVERSATION FLOW:

            FIRST MESSAGE (No history):
            Hi! I'm {agent_name}.

            **[Identified Issue Type]:**
            - Ask ONE clear diagnostic question only

            FOLLOW-UP MESSAGE (History exists):

            **[Action or Finding]**

            1. Provide ONE action to try

            - Ask ONE confirmation question

            NEVER IN FOLLOW-UPS:
            - No greetings
            - No multiple questions
            - No restarting the conversation

            10. FINAL SUMMARY (ONLY when user says bye / done / thank you):

            **Issue Summary:**
            - Department: [Name]
            - Priority: [Low / Medium / High / Critical]
            - Status: [Resolved / Ticket Raised]

            REMEMBER:
            - One question at a time
            - Action → confirmation → next step
            - No assumptions, no guessing
            - Think like a real banking IT support engineer
            - Your name is "{agent_name}"
        """

# Global instance
groq_service = GroqService() if llm_settings.LLM_PROVIDER == "groq" else None
