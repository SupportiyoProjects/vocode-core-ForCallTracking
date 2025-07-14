"""
Example script demonstrating how to use the call tracking functionality
for outbound calls in Vocode.

This example shows how the call tracker automatically logs:
- Call start time
- Agent start time (when agent begins first operation)
- Call end time
- Total call duration
- Agent operation duration

The tracking is automatically integrated into the OutboundCall class.
"""

import asyncio
import os
from vocode.streaming.models.agent import ChatGPTAgentConfig
from vocode.streaming.models.synthesizer import ElevenLabsSynthesizerConfig
from vocode.streaming.models.telephony import TwilioConfig
from vocode.streaming.models.transcriber import DeepgramTranscriberConfig
from vocode.streaming.telephony.config_manager.redis_config_manager import RedisConfigManager
from vocode.streaming.telephony.conversation.outbound_call import OutboundCall
from vocode.streaming.utils.call_tracker import call_tracker


async def make_tracked_outbound_call():
    """
    Example function showing how to make an outbound call with automatic tracking.
    The call tracker will automatically log:
    - When the call starts
    - When the agent begins its first operation
    - When the call ends
    - Total duration and timing information
    """
    
    # Configuration for the outbound call
    config_manager = RedisConfigManager()
    
    # Agent configuration (using ChatGPT)
    agent_config = ChatGPTAgentConfig(
        initial_message="Hello! This is a test call with tracking enabled.",
        prompt_preamble="You are a helpful assistant making a test call."
    )
    
    # Telephony configuration (Twilio)
    telephony_config = TwilioConfig(
        account_sid=os.getenv("TWILIO_ACCOUNT_SID"),
        auth_token=os.getenv("TWILIO_AUTH_TOKEN"),
    )
    
    # Create the outbound call - tracking is automatically integrated
    outbound_call = OutboundCall(
        base_url="https://your-app.ngrok.io",  # Replace with your webhook URL
        to_phone="+1234567890",  # Replace with destination phone number
        from_phone="+0987654321",  # Replace with your Twilio phone number
        config_manager=config_manager,
        agent_config=agent_config,
        telephony_config=telephony_config,
    )
    
    try:
        # Start the call - this will automatically log the start time
        print("Starting outbound call...")
        await outbound_call.start()
        print(f"Call started with conversation ID: {outbound_call.conversation_id}")
        
        # You can check the current status of the call
        status = call_tracker.get_call_status(outbound_call.conversation_id)
        print(f"Current call status: {status}")
        
        # Simulate call duration (in real usage, this would be the actual call)
        print("Simulating call duration...")
        await asyncio.sleep(30)  # Simulate 30-second call
        
        # End the call - this will automatically log the end time and duration
        print("Ending call...")
        await outbound_call.end()
        print("Call ended successfully")
        
    except Exception as e:
        print(f"Error during call: {e}")
        # Even if there's an error, try to end the call for proper tracking
        try:
            await outbound_call.end()
        except:
            pass


async def check_active_calls():
    """
    Example function showing how to check currently active calls.
    """
    active_calls = call_tracker.get_active_calls()
    print(f"Currently active calls: {len(active_calls)}")
    
    for conv_id, call_data in active_calls.items():
        print(f"Call {conv_id}:")
        print(f"  From: {call_data['from_phone']}")
        print(f"  To: {call_data['to_phone']}")
        print(f"  Duration: {call_data['current_duration']:.2f}s")
        print(f"  Agent started: {call_data['agent_started']}")


if __name__ == "__main__":
    # Example usage
    asyncio.run(make_tracked_outbound_call())
    
    # Check for any remaining active calls
    asyncio.run(check_active_calls())