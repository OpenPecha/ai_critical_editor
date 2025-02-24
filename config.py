import os
import anthropic
from langchain_anthropic import ChatAnthropic

ANTHROPIC_KEY = os.getenv("ANTHROPIC_KEY")

LLM = ChatAnthropic(model="claude-3-5-sonnet-latest",max_tokens=7000, api_key=ANTHROPIC_KEY)