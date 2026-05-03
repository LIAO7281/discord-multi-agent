# Custom Agent Example - 自定义 Agent 示例

This example shows how to create a custom agent by extending the `BaseAgent` class.

## Use Case: Sentiment Analysis Agent

Let's create a `SentimentAgent` that analyzes the emotional tone of user messages.

## Step 1: Create the Agent

**`src/agents/sentiment_agent.py`**:

```python
"""
Sentiment Analysis Agent
Analyzes the emotional tone of user messages.
"""
import json
import os
from typing import Dict, Any

from src.agents.base_agent import BaseAgent


class SentimentAgent(BaseAgent):
    """
    Agent for analyzing message sentiment.
    
    This agent uses LLM to determine if a message is:
    - positive (积极)
    - negative (消极)
    - neutral (中性)
    - urgent (紧急)
    """
    
    def __init__(self):
        """Initialize the Sentiment Agent."""
        system_prompt = """You are a sentiment analysis expert.
Analyze the emotional tone of the user's message.
Return a JSON object with:
- "sentiment": "positive|negative|neutral|urgent"
- "confidence": 0.0-1.0
- "emotions": ["emotion1", "emotion2"]
- "priority_adjustment": -1|0|+1  (-1=lower priority, +1=raise priority)
"""
        
        super().__init__(
            name="SentimentAgent",
            system_prompt=system_prompt,
            model=os.getenv("HERMES_MODEL", "deepseek-chat"),
            temperature=0.3,  # Low temperature for consistent results
            max_tokens=300
        )
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message and return sentiment analysis.
        
        Args:
            input_data: Dictionary containing:
                - "message": User's message text
                - "user_id": Discord user ID (optional)
                
        Returns:
            Dictionary containing:
                - "sentiment": Detected sentiment
                - "confidence": Confidence score
                - "emotions": List of detected emotions
                - "priority_adjustment": Priority adjustment suggestion
        """
        message = input_data.get("message", "")
        user_id = input_data.get("user_id", "unknown")
        
        # Build prompt
        prompt = f"""Analyze the sentiment of this message:
Message: {message}

Return ONLY a valid JSON object in this exact format:
{{"sentiment": "positive|negative|neutral|urgent", "confidence": 0.0-1.0, "emotions": ["emotion1"], "priority_adjustment": -1|0|+1}}
"""
        
        # Call LLM
        response = self._call_hermes(prompt)
        
        try:
            # Parse JSON response
            result = json.loads(response)
            
            # Validate result
            if "sentiment" not in result:
                result["sentiment"] = "neutral"
            if "confidence" not in result:
                result["confidence"] = 0.5
            if "emotions" not in result:
                result["emotions"] = []
            if "priority_adjustment" not in result:
                result["priority_adjustment"] = 0
            
            return result
            
        except json.JSONDecodeError:
            # Fallback: return defaultValues
            self.logger.error(f"Failed to parse LLM response: {response}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "emotions": [],
                "priority_adjustment": 0,
                "error": "Failed to parse LLM response"
            }
```

## Step 2: Integrate into Bot

**Modify `src/bot.py` to use the new agent**:

```python
# Add import
from src.agents.sentiment_agent import SentimentAgent

# Initialize in __init__
self.sentiment_agent = SentimentAgent()

# Use in on_message
@bot.event
async def on_message(message):
    # ... existing code ...
    
    # Step 0.5: Sentiment Analysis (NEW!)
    sentiment_result = self.sentiment_agent.process({
        "message": message.content,
        "user_id": str(message.author.id)
    })
    
    self.logger.info(f"Sentiment: {sentiment_result['sentiment']} (confidence: {sentiment_result['confidence']})")
    
    # Adjust priority based on sentiment
    priority = intent_result.get("priority", "normal")
    adjustment = sentiment_result.get("priority_adjustment", 0)
    
    if adjustment == 1 or sentiment_result["sentiment"] == "urgent":
        priority = "high"
    elif adjustment == -1:
        priority = "low"
    
    # ... continue with existing workflow ...
```

## Step 3: Test the Agent

**Create `tests/test_sentiment_agent.py`**:

```python
"""
Tests for Sentiment Analysis Agent
"""
import unittest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.sentiment_agent import SentimentAgent


class TestSentimentAgent(unittest.TestCase):
    """Test cases for SentimentAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent = SentimentAgent()
    
    @patch('src.agents.base_agent.BaseAgent._call_hermes')
    def test_positive_sentiment(self, mock_call):
        """Test positive sentiment detection."""
        mock_call.return_value = '{"sentiment": "positive", "confidence": 0.95, "emotions": ["happy", "satisfied"], "priority_adjustment": 0}'
        
        result = self.agent.process({
            "message": "I love this product! It's amazing!",
            "user_id": "test_user"
        })
        
        self.assertEqual(result["sentiment"], "positive")
        self.assertGreater(result["confidence"], 0.8)
        self.assertIn("happy", result["emotions"])
    
    @patch('src.agents.base_agent.BaseAgent._call_hermes')
    def test_negative_sentiment(self, mock_call):
        """Test negative sentiment detection."""
        mock_call.return_value = '{"sentiment": "negative", "confidence": 0.9, "emotions": ["frustrated", "angry"], "priority_adjustment": 1}'
        
        result = self.agent.process({
            "message": "This is terrible! Nothing works!",
            "user_id": "test_user"
        })
        
        self.assertEqual(result["sentiment"], "negative")
        self.assertEqual(result["priority_adjustment"], 1)  # Should raise priority
    
    @patch('src.agents.base_agent.BaseAgent._call_hermes')
    def test_urgent_sentiment(self, mock_call):
        """Test urgent sentiment detection."""
        mock_call.return_value = '{"sentiment": "urgent", "confidence": 0.95, "emotions": ["panicked"], "priority_adjustment": 1}'
        
        result = self.agent.process({
            "message": "Emergency! The server is down!",
            "user_id": "test_user"
        })
        
        self.assertEqual(result["sentiment"], "urgent")
        self.assertEqual(result["priority_adjustment"], 1)
    
    def test_invalid_json_response(self):
        """Test handling of invalid JSON response."""
        with patch('src.agents.base_agent.BaseAgent._call_hermes') as mock_call:
            mock_call.return_value = "This is not JSON"
            
            result = self.agent.process({
                "message": "Test message",
                "user_id": "test_user"
            })
            
            # Should return default values
            self.assertEqual(result["sentiment"], "neutral")
            self.assertEqual(result["confidence"], 0.0)
            self.assertIn("error", result)


if __name__ == '__main__':
    unittest.main()
```

## Step 4: Run Tests

```bash
# Run sentiment agent tests
python -m pytest tests/test_sentiment_agent.py -v

# Run all tests
python -m pytest tests/ -v
```

## Advanced: Creating a Translation Agent

Here's another example: a `TranslationAgent` for multi-language support.

**`src/agents/translation_agent.py`**:

```python
"""
Translation Agent
Translates messages to different languages.
"""
import json
import os
from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent


class TranslationAgent(BaseAgent):
    """Agent for translating text between languages."""
    
    def __init__(self):
        """Initialize the Translation Agent."""
        system_prompt = """You are a professional translator.
Translate the given text to the target language.
Maintain the original tone and meaning.
"""
        
        super().__init__(
            name="TranslationAgent",
            system_prompt=system_prompt,
            model=os.getenv("HERMES_MODEL", "deepseek-chat"),
            temperature=0.3,
            max_tokens=1000
        )
        
        # Supported languages
        self.supported_languages = {
            "zh": "Chinese (Simplified)",
            "en": "English",
            "ja": "Japanese",
            "ko": "Korean",
            "es": "Spanish",
            "fr": "French",
            "de": "German"
        }
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate text to target language.
        
        Args:
            input_data: Dictionary containing:
                - "text": Text to translate
                - "target_language": Target language code (e.g., "zh", "en")
                - "source_language": Source language (optional, auto-detect if not provided)
                
        Returns:
            Dictionary containing:
                - "translation": Translated text
                - "source_language": Detected/source language
                - "target_language": Target language
                - "confidence": Translation confidence
        """
        text = input_data.get("text", "")
        target_lang = input_data.get("target_language", "en")
        source_lang = input_data.get("source_language", "auto")
        
        # Validate target language
        if target_lang not in self.supported_languages:
            return {
                "translation": "",
                "error": f"Unsupported target language: {target_lang}",
                "supported_languages": self.supported_languages
            }
        
        # Build prompt
        prompt = f"""Translate the following text to {self.supported_languages[target_lang]}:

Text: {text}
Target Language: {self.supported_languages[target_lang]}

Return ONLY the translation, no additional text.
"""
        
        # Call LLM
        translation = self._call_hermes(prompt)
        
        return {
            "translation": translation.strip(),
            "source_language": source_lang,
            "target_language": target_lang,
            "confidence": 0.95  # Placeholder - could use another LLM call to verify
        }
    
    def batch_translate(self, texts: List[str], target_language: str) -> List[Dict[str, Any]]:
        """
        Translate multiple texts to target language.
        
        Args:
            texts: List of texts to translate
            target_language: Target language code
            
        Returns:
            List of translation results
        """
        results = []
        for text in texts:
            result = self.process({
                "text": text,
                "target_language": target_language
            })
            results.append(result)
        return results
```

## Best Practices for Custom Agents

1. **Clear Responsibility**: Each agent should have a single, well-defined responsibility
2. **Consistent Input/Output**: Use consistent data structures for `process()` method
3. **Error Handling**: Always handle LLM errors gracefully
4. **Logging**: Add informative log messages
5. **Testing**: Write comprehensive unit tests
6. **Documentation**: Document your agent's purpose and usage

---

**Next Steps**:
- Read `docs/architecture.md` for system design details
- Check `tests/test_agents.py` for more test examples
- Join our Discord for help: https://discord.gg/yourserver
