import time
from datetime import datetime
from typing import Dict, Optional

from loguru import logger


class CallTracker:
    """
    A utility class to track call timing and duration for outbound calls.
    Provides logging functionality to track when calls start, end, and their total duration.
    """
    
    def __init__(self):
        self._call_sessions: Dict[str, Dict[str, any]] = {}
    
    def start_call_tracking(self, conversation_id: str, to_phone: str, from_phone: str) -> None:
        """
        Start tracking a call session.
        
        Args:
            conversation_id: Unique identifier for the conversation
            to_phone: The phone number being called
            from_phone: The calling phone number
        """
        start_time = time.time()
        start_datetime = datetime.now()
        
        self._call_sessions[conversation_id] = {
            'start_time': start_time,
            'start_datetime': start_datetime,
            'to_phone': to_phone,
            'from_phone': from_phone,
            'agent_started': False,
            'agent_start_time': None,
            'end_time': None,
            'end_datetime': None,
            'duration': None
        }
        
        logger.info(
            f"📞 CALL STARTED - ID: {conversation_id} | "
            f"FROM: {from_phone} | TO: {to_phone} | "
            f"START TIME: {start_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
        )
    
    def mark_agent_started(self, conversation_id: str) -> None:
        """
        Mark when the agent starts its first operation.
        
        Args:
            conversation_id: Unique identifier for the conversation
        """
        # Try to find the session by conversation_id or by any session that doesn't have agent_started yet
        session_key = None
        if conversation_id in self._call_sessions:
            session_key = conversation_id
        else:
            # Look for any active session without agent started (most recent)
            for key, session in self._call_sessions.items():
                if not session['agent_started'] and session['end_time'] is None:
                    session_key = key
                    logger.info(f"🔗 Linking conversation {conversation_id} to call session {key}")
                    break
        
        if session_key is None:
            logger.warning(f"Call session {conversation_id} not found for agent start tracking")
            return
            
        agent_start_time = time.time()
        agent_start_datetime = datetime.now()
        
        self._call_sessions[session_key]['agent_started'] = True
        self._call_sessions[session_key]['agent_start_time'] = agent_start_time
        
        session = self._call_sessions[session_key]
        call_setup_duration = agent_start_time - session['start_time']
        
        logger.info(
            f"🤖 AGENT STARTED - ID: {conversation_id} | "
            f"AGENT START TIME: {agent_start_datetime.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"CALL SETUP DURATION: {call_setup_duration:.2f}s"
        )
    
    def end_call_tracking(self, conversation_id: str) -> Optional[Dict[str, any]]:
        """
        End tracking a call session and log the summary.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Dictionary containing call timing information or None if session not found
        """
        # Try to find the session by conversation_id or by any active session
        session_key = None
        if conversation_id in self._call_sessions:
            session_key = conversation_id
        else:
            # Look for any active session (not yet ended)
            for key, session in self._call_sessions.items():
                if session['end_time'] is None:
                    session_key = key
                    logger.info(f"🔗 Ending call session {key} for conversation {conversation_id}")
                    break
        
        if session_key is None:
            logger.warning(f"Call session {conversation_id} not found for end tracking")
            return None
            
        end_time = time.time()
        end_datetime = datetime.now()
        
        session = self._call_sessions[session_key]
        session['end_time'] = end_time
        session['end_datetime'] = end_datetime
        session['duration'] = end_time - session['start_time']
        
        # Calculate different duration metrics
        total_duration = session['duration']
        agent_duration = None
        if session['agent_started'] and session['agent_start_time']:
            agent_duration = end_time - session['agent_start_time']
        
        logger.info(
            f"📞 CALL ENDED - ID: {conversation_id} | "
            f"FROM: {session['from_phone']} | TO: {session['to_phone']} | "
            f"START TIME: {session['start_datetime'].strftime('%Y-%m-%d %H:%M:%S')} | "
            f"END TIME: {end_datetime.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"TOTAL DURATION: {total_duration:.2f}s ({total_duration/60:.2f}m)" +
            (f" | AGENT DURATION: {agent_duration:.2f}s" if agent_duration else " | AGENT NEVER STARTED")
        )
        
        # Clean up the session and return the data
        call_data = self._call_sessions.pop(session_key)
        return call_data
    
    def get_call_status(self, conversation_id: str) -> Optional[Dict[str, any]]:
        """
        Get current status of a call session.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Dictionary containing current call information or None if session not found
        """
        if conversation_id not in self._call_sessions:
            return None
            
        session = self._call_sessions[conversation_id].copy()
        if session['end_time'] is None:
            # Call is still active, calculate current duration
            current_time = time.time()
            session['current_duration'] = current_time - session['start_time']
            
        return session
    
    def get_active_calls(self) -> Dict[str, Dict[str, any]]:
        """
        Get all currently active call sessions.
        
        Returns:
            Dictionary of active call sessions
        """
        active_calls = {}
        current_time = time.time()
        
        for conv_id, session in self._call_sessions.items():
            if session['end_time'] is None:
                session_copy = session.copy()
                session_copy['current_duration'] = current_time - session['start_time']
                active_calls[conv_id] = session_copy
                
        return active_calls


# Global instance for use across the application
call_tracker = CallTracker()