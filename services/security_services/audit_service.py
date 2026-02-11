"""
Security Audit Service
Monitors and logs security events
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict

from core.logging.logger import security_logger


class SecurityAuditService:
    """
    Security Audit and Monitoring Service
    Tracks security events, failed login attempts, and suspicious activities
    """
    
    def __init__(self):
        """Initialize security audit service"""
        self.failed_attempts: Dict[str, List[datetime]] = defaultdict(list)
        self.blocked_users: Dict[str, datetime] = {}
        self.max_failed_attempts = 5
        self.block_duration_minutes = 30
    
    async def log_login_attempt(self, user_id: str, success: bool, ip_address: str):
        """
        Log login attempt
        
        Args:
            user_id: User identifier
            success: Whether login was successful
            ip_address: IP address of the request
        """
        if success:
            # Clear failed attempts on successful login
            if user_id in self.failed_attempts:
                del self.failed_attempts[user_id]
            
            security_logger.info(
                f"Successful login",
                method="LOGIN",
                extra_info={"user_id": user_id, "ip": ip_address}
            )
        else:
            # Track failed attempt
            self.failed_attempts[user_id].append(datetime.utcnow())
            
            # Check if user should be blocked
            if len(self.failed_attempts[user_id]) >= self.max_failed_attempts:
                await self.block_user(user_id, ip_address)
            
            security_logger.warning(
                f"Failed login attempt",
                method="LOGIN",
                extra_info={
                    "user_id": user_id,
                    "ip": ip_address,
                    "attempt_count": len(self.failed_attempts[user_id])
                }
            )
    
    async def block_user(self, user_id: str, ip_address: str):
        """
        Temporarily block user due to too many failed attempts
        
        Args:
            user_id: User identifier
            ip_address: IP address
        """
        block_until = datetime.utcnow() + timedelta(minutes=self.block_duration_minutes)
        self.blocked_users[user_id] = block_until
        
        security_logger.critical(
            f"User blocked due to multiple failed login attempts",
            method="BLOCK_USER",
            extra_info={
                "user_id": user_id,
                "ip": ip_address,
                "blocked_until": block_until.isoformat(),
                "failed_attempts": len(self.failed_attempts[user_id])
            }
        )
    
    async def is_user_blocked(self, user_id: str) -> bool:
        """
        Check if user is currently blocked
        
        Args:
            user_id: User identifier
            
        Returns:
            bool: True if user is blocked
        """
        if user_id not in self.blocked_users:
            return False
        
        block_until = self.blocked_users[user_id]
        
        if datetime.utcnow() >= block_until:
            # Block period expired
            del self.blocked_users[user_id]
            if user_id in self.failed_attempts:
                del self.failed_attempts[user_id]
            return False
        
        return True
    
    async def log_data_access(self, user_id: str, resource: str, action: str, ip_address: str):
        """
        Log data access for audit trail
        
        Args:
            user_id: User identifier
            resource: Resource being accessed
            action: Action performed (read, write, delete)
            ip_address: IP address
        """
        security_logger.info(
            f"Data access",
            method=action.upper(),
            extra_info={
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "ip": ip_address
            }
        )
    
    async def log_suspicious_activity(self, user_id: str, activity: str, 
                                     details: Dict, ip_address: str):
        """
        Log suspicious activity
        
        Args:
            user_id: User identifier
            activity: Type of suspicious activity
            details: Additional details
            ip_address: IP address
        """
        security_logger.warning(
            f"Suspicious activity detected: {activity}",
            method="SECURITY_ALERT",
            extra_info={
                "user_id": user_id,
                "activity": activity,
                "details": details,
                "ip": ip_address
            }
        )
    
    async def get_security_events(self, user_id: Optional[str] = None, 
                                 hours: int = 24) -> List[Dict]:
        """
        Get recent security events
        
        Args:
            user_id: Filter by user ID (optional)
            hours: Number of hours to look back
            
        Returns:
            List[Dict]: List of security events
        """
        # Placeholder - In production, read from database
        # This would query the security logs
        
        return []
    
    async def generate_security_report(self, days: int = 7) -> Dict:
        """
        Generate security report for specified period
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Dict: Security report
        """
        report = {
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat(),
            "total_login_attempts": 0,
            "failed_login_attempts": 0,
            "blocked_users_count": len(self.blocked_users),
            "suspicious_activities": 0,
            "data_access_events": 0
        }
        
        security_logger.info(
            "Security report generated",
            method="REPORT",
            extra_info={"days": days}
        )
        
        return report
