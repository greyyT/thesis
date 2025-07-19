import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import chainlit as cl
from typing import Optional, Dict, Any, Union
import asyncio

# Load environment variables
load_dotenv()

# Initialize OpenAI client with OpenRouter configuration
client = AsyncOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"), base_url="https://openrouter.ai/api/v1"
)

# Model to use
MODEL_NAME = "openai/gpt-4.1-mini"

# Configuration
APPROVAL_REQUIRED = True  # Toggle for human approval
DEFAULT_TIMEOUT = 30  # seconds


# Helper functions for human-in-the-loop
async def ask_for_approval(content: str, context: str = "") -> Union[bool, str]:
    """Ask user for approval before proceeding with an action."""
    try:
        res = await cl.AskActionMessage(
            content=f"**AI Response Preview:**\n\n{content}\n\n{context}\n\nDo you want me to proceed with this response?",
            actions=[
                cl.Action(
                    name="approve",
                    value="approve",
                    label="✅ Approve & Send"
                ),
                cl.Action(
                    name="modify",
                    value="modify",
                    label="✏️ Modify Response"
                ),
                cl.Action(
                    name="reject",
                    value="reject",
                    label="❌ Reject & Retry"
                ),
            ],
            timeout=DEFAULT_TIMEOUT,
        ).send()
        
        if res and res.get("value") == "approve":
            return True
        elif res and res.get("value") == "modify":
            modified = await ask_for_modification(content)
            return modified if modified else False
        else:
            return False
    except asyncio.TimeoutError:
        await cl.Message(content="⏱️ Approval timeout. Proceeding with caution...").send()
        return True


async def ask_for_modification(original_content: str) -> Optional[str]:
    """Ask user to modify the AI response."""
    res = await cl.AskUserMessage(
        content="Please provide your modified version of the response:",
        timeout=60,
    ).send()
    
    if res:
        return res.get("output")
    return None


async def ask_for_clarification(query: str) -> Optional[str]:
    """Ask user for clarification when input is ambiguous."""
    res = await cl.AskUserMessage(
        content=f"I need clarification on: **{query}**\n\nCould you please provide more details?",
        timeout=DEFAULT_TIMEOUT,
    ).send()
    
    if res:
        return res.get("output")
    return None


async def ask_for_file_context() -> Optional[Dict[str, Any]]:
    """Ask user to upload a file for additional context."""
    res = await cl.AskFileMessage(
        content="Would you like to upload a file for additional context?",
        accept=["text/plain", "application/pdf", ".txt", ".md", ".csv"],
        max_size_mb=10,
        timeout=DEFAULT_TIMEOUT,
    ).send()
    
    if res and res.get("files"):
        file = res["files"][0]
        return {
            "name": file.name,
            "path": file.path,
            "size": file.size,
            "type": file.type,
        }
    return None


async def get_ai_response(messages: list, temperature: float = 0.7) -> str:
    """Get response from AI model."""
    try:
        stream = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            stream=True,
            temperature=temperature,
        )
        
        response_content = ""
        msg = cl.Message(content="")
        await msg.send()
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                response_content += chunk.choices[0].delta.content
                await msg.stream_token(chunk.choices[0].delta.content)
        
        await msg.update()
        return response_content
    except Exception as e:
        error_msg = f"Error getting AI response: {str(e)}"
        await cl.Message(content=error_msg).send()
        raise


@cl.on_message
async def main(message: cl.Message):
    """Main handler for incoming messages with human-in-the-loop."""
    user_message = message.content
    
    # Handle commands
    if user_message.startswith("/"):
        if user_message.lower() == "/toggle-approval":
            await toggle_approval_callback(None)
            return
        elif user_message.lower() == "/clear":
            await clear_history_callback(None)
            return
        elif user_message.lower() == "/help":
            await show_help_callback(None)
            return
        else:
            await cl.Message(content="❓ Unknown command. Type `/help` for available commands.").send()
            return
    
    # Store conversation in session
    if not cl.user_session.get("messages"):
        cl.user_session.set("messages", [])
    
    messages = cl.user_session.get("messages")
    messages.append({"role": "user", "content": user_message})
    
    # Check if we need clarification for vague queries
    vague_indicators = ["something", "that thing", "it", "stuff", "whatever"]
    if any(indicator in user_message.lower() for indicator in vague_indicators) and len(user_message.split()) < 10:
        clarification = await ask_for_clarification(user_message)
        if clarification:
            user_message = f"{user_message} (Clarification: {clarification})"
            messages[-1]["content"] = user_message
            await cl.Message(content=f"📝 Got it! Processing: *{user_message}*").send()
    
    # Ask if user wants to provide file context
    if any(word in user_message.lower() for word in ["analyze", "review", "check", "file", "document"]):
        file_info = await ask_for_file_context()
        if file_info:
            await cl.Message(
                content=f"📎 File received: **{file_info['name']}** ({file_info['size']} bytes)"
            ).send()
            messages.append({
                "role": "system",
                "content": f"User provided file: {file_info['name']} for context"
            })
    
    try:
        # Get AI response first (without sending)
        thinking_msg = cl.Message(content="🤔 Thinking...")
        await thinking_msg.send()
        
        response_content = ""
        stream = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            stream=True,
            temperature=0.7,
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                response_content += chunk.choices[0].delta.content
        
        await thinking_msg.remove()
        
        # Check if approval is required
        approval_mode = cl.user_session.get("approval_mode", APPROVAL_REQUIRED)
        if approval_mode:
            # Determine if this action needs approval
            needs_approval = any(
                keyword in response_content.lower()
                for keyword in ["execute", "run", "delete", "modify", "create", "update", "send", "api", "database"]
            )
            
            if needs_approval:
                approval_result = await ask_for_approval(
                    response_content,
                    context="⚠️ This response contains potentially sensitive actions."
                )
                
                if isinstance(approval_result, str):  # Modified response
                    response_content = approval_result
                elif not approval_result:  # Rejected
                    await cl.Message(
                        content="❌ Response rejected. Let me try a different approach..."
                    ).send()
                    # Retry with more conservative parameters
                    messages.append({
                        "role": "system",
                        "content": "Previous response was rejected. Provide a more conservative alternative."
                    })
                    response_content = await get_ai_response(messages, temperature=0.3)
                    # Remove the system message
                    messages.pop()
        
        # Send the final response
        final_msg = cl.Message(content=response_content)
        await final_msg.send()
        
        # Update conversation history
        messages.append({"role": "assistant", "content": response_content})
        cl.user_session.set("messages", messages)
        
    except Exception as e:
        await cl.Message(content=f"❌ Error: {str(e)}").send()


@cl.on_chat_start
async def start():
    """Handler for when a chat session starts."""
    # Initialize session
    cl.user_session.set("messages", [])
    cl.user_session.set("approval_mode", APPROVAL_REQUIRED)
    
    # Send welcome message with instructions
    welcome_message = f"""👋 Welcome! I'm connected to **{MODEL_NAME}** via OpenRouter with human-in-the-loop features.

**Available Features:**
• 🔒 **Approval Mode**: {' ON' if APPROVAL_REQUIRED else ' OFF'} - I'll ask for your approval before sensitive actions
• 🤔 **Clarification Requests**: I'll ask for more details when your request is unclear
• 📎 **File Context**: You can upload files for additional context
• ✏️ **Response Modification**: You can modify my responses before they're finalized

**Quick Commands:**
• Type `/toggle-approval` to turn approval mode on/off
• Type `/clear` to clear conversation history
• Type `/help` for more information

How can I help you today?"""
    
    await cl.Message(content=welcome_message).send()
    
    # Add action buttons
    actions = [
        cl.Action(
            name="toggle_approval",
            value="toggle",
            label="🔄 Toggle Approval Mode"
        ),
        cl.Action(
            name="clear_history",
            value="clear",
            label="🗑️ Clear History"
        ),
        cl.Action(
            name="show_help",
            value="help",
            label="❓ Help"
        ),
    ]
    
    await cl.Message(
        content="Quick actions:",
        actions=actions
    ).send()


@cl.action_callback("toggle_approval")
async def toggle_approval_callback(action: cl.Action):
    """Toggle approval mode on/off."""
    current_mode = cl.user_session.get("approval_mode")
    new_mode = not current_mode
    cl.user_session.set("approval_mode", new_mode)
    
    global APPROVAL_REQUIRED
    APPROVAL_REQUIRED = new_mode
    
    await cl.Message(
        content=f"🔄 Approval mode is now **{'ON' if new_mode else 'OFF'}**"
    ).send()


@cl.action_callback("clear_history")
async def clear_history_callback(action: cl.Action):
    """Clear conversation history."""
    cl.user_session.set("messages", [])
    await cl.Message(content="🗑️ Conversation history cleared!").send()


@cl.action_callback("show_help")
async def show_help_callback(action: cl.Action):
    """Show help information."""
    help_text = """**🤖 Human-in-the-Loop Features Help**

**1. Approval Mode**
When enabled, I'll ask for your approval before:
- Executing commands
- Making API calls
- Modifying data
- Performing sensitive actions

**2. Clarification Requests**
I'll automatically ask for clarification when:
- Your message is vague or ambiguous
- Important details are missing
- Multiple interpretations are possible

**3. File Upload**
When your message mentions analysis or files:
- I'll offer to let you upload relevant files
- Supported formats: .txt, .md, .csv, .pdf
- Max size: 10MB

**4. Response Modification**
During approval:
- ✅ Approve: Send the response as-is
- ✏️ Modify: Edit the response before sending
- ❌ Reject: Ask me to try a different approach

**5. Conversation Management**
- All conversations are stored in session
- Use `/clear` or the Clear History button to reset
- Toggle approval mode with `/toggle-approval`

**Tips:**
- Be specific in your requests to avoid clarification prompts
- Upload relevant files when asking for analysis
- Use approval mode for sensitive operations
- Modify responses to better fit your needs"""
    
    await cl.Message(content=help_text).send()
