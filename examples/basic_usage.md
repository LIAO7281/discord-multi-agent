# Example 1: Basic Usage - 基础使用示例

This example demonstrates the basic usage of the Discord Multi-Agent System.

## Prerequisites

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your Discord token and API keys
```

3. Set up Discord Bot:
   - Go to https://discord.com/developers/applications
   - Create a new application
   - Add a Bot
   - Enable "MESSAGE CONTENT INTENT" under the "Bot" tab
   - Invite the bot to your server using OAuth2 URL Generator

## Running the Bot

```bash
python src/bot.py
```

## Testing the Bot

Once the bot is running, you can test it by sending messages in your Discord server:

### Test Case 1: Technical Support
```
User: My installation failed, what should I do?
Bot: Hello! Installation failure may be caused by several reasons:
      1. System requirements not met
      2. Corrupted installation package
      3. Permission issues
      ...
```

### Test Case 2: Product Inquiry
```
User: How much does the premium plan cost?
Bot: The premium plan is $9.99/month and includes...
```

### Test Case 3: Human Handoff
```
User: I want to speak to a human
Bot: I'll connect you with a human agent. Please wait...
```

## Code Example: Using Agents Directly

You can also use the agents directly in your Python code:

```python
import os
import sys
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.intent_agent import IntentAgent
from src.agents.reply_agent import ReplyAgent
from src.agents.quality_agent import QualityAgent

# Initialize agents
intent_agent = IntentAgent()
reply_agent = ReplyAgent()
quality_agent = QualityAgent()

# Step 1: Intent Recognition
message = "My software installation failed, what should I do?"
print(f"User Message: {message}")

intent_result = intent_agent.process({
    "message": message,
    "user_id": "test_user_123"
})

print(f"\nIntent Result:")
print(json.dumps(intent_result, indent=2, ensure_ascii=False))

# Step 2: Reply Generation
reply_result = reply_agent.process({
    "message": message,
    "intent": intent_result,
    "user_id": "test_user_123"
})

print(f"\nReply Result:")
print(json.dumps(reply_result, indent=2, ensure_ascii=False))

# Step 3: Quality Check
quality_result = quality_agent.process({
    "original_message": message,
    "intent": intent_result,
    "reply": reply_result["reply"],
    "user_id": "test_user_123"
})

print(f"\nQuality Result:")
print(json.dumps(quality_result, indent=2, ensure_ascii=False))

# Step 4: Final Action
action = quality_result["action"]
if action == "send":
    print(f"\nFinal Reply: {quality_result['final_reply']}")
elif action == "rewrite":
    print(f"\nRewritten Reply: {quality_result['final_reply']}")
elif action == "human":
    print("\nAction: Transfer to human agent")
```

## Adding Knowledge Base Documents

Create Markdown files in the `knowledge_base/` directory:

**knowledge_base/install.md**:
```markdown
# Installation Guide

## System Requirements
- Windows 10/11, macOS 10.15+, or Linux
- 8GB RAM minimum
- 5GB free disk space

## Installation Steps
1. Download the installer from our website
2. Run the installer as administrator
3. Follow the on-screen instructions
4. Restart your computer

## Common Issues
### Installation Fails
- Ensure you have administrator privileges
- Check if antivirus is blocking the installer
- Verify system meets minimum requirements
```

**knowledge_base/faq.md**:
```markdown
# Frequently Asked Questions

## Pricing
- Basic Plan: Free
- Premium Plan: $9.99/month
- Enterprise Plan: Contact sales

## Refund Policy
- 30-day money-back guarantee
- No questions asked

## Account Management
- How to reset password
- How to delete account
- How to change email
```

## Monitoring and Debugging

### View Logs

The bot logs to both console and `bot.log`:

```bash
# View real-time logs
tail -f bot.log

# Filter logs by level
grep "ERROR" bot.log
grep "WARNING" bot.log
```

### Enable Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env`:

```env
LOG_LEVEL=DEBUG
```

This will print detailed information about:
- Agent processing steps
- LLM API calls
- RAG search results
- Quality check details

## Next Steps

- Customize agent prompts in `src/agents/*_agent.py`
- Add more knowledge base documents
- Implement custom agents by extending `BaseAgent`
- Deploy to a cloud server for 24/7 operation

## Troubleshooting

### Bot doesn't respond
- Check if bot is online (green status in Discord)
- Verify bot has "SEND MESSAGES" permission in the channel
- Check `DISCORD_TOKEN` in `.env` is correct

### LLM API errors
- Verify `OPENAI_API_KEY` is valid
- Check `OPENAI_BASE_URL` is correct for your LLM provider
- Ensure you have sufficient API credits

### Knowledge base not working
- Verify `KNOWLEDGE_BASE_PATH` in `.env` points to correct directory
- Ensure knowledge base files are in `.md` or `.txt` format
- Check file encoding is UTF-8

---

**Need Help?**

- Open an issue: https://github.com/yourusername/discord-multi-agent/issues
- Join Discord: https://discord.gg/yourserver
