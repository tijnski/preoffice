#!/usr/bin/env python3
"""
PrePanda AI Service for PreOffice
Connects to Venice.ai API for AI-powered writing assistance

This module provides the backend service for the PrePanda AI Assistant,
handling API communication with Venice.ai and document context processing.
"""

import json
import os
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field


@dataclass
class Message:
    """Chat message structure"""
    role: str  # 'user', 'assistant', or 'system'
    content: str


@dataclass
class PrePandaConfig:
    """Configuration for PrePanda service"""
    api_url: str = "https://api.venice.ai/api/v1"
    api_key: str = ""
    model_smart: str = "llama-3.2-3b"
    model_ask: str = "llama-3.3-70b"
    temperature: float = 0.7
    max_tokens: int = 500
    max_tokens_ask: int = 1000


class PrePandaService:
    """
    PrePanda AI Service
    Handles communication with Venice.ai API for AI-powered features
    """

    SYSTEM_PROMPT = """You are PrePanda, an AI writing assistant for PreOffice (part of the Presearch Pre-suite).
You help users with document writing, editing, summarizing, and improving their text.
Be helpful, concise, and professional. Use markdown formatting when appropriate.
When improving text, maintain the original meaning while enhancing clarity and style."""

    PROMPTS = {
        "summarize": "Please provide a concise summary of the following text, highlighting the key points:\n\n{text}",
        "improve": "Please improve the following text, making it clearer, more professional, and better structured. Return only the improved text:\n\n{text}",
        "translate": "Please translate the following text to {language}. Return only the translation:\n\n{text}",
        "explain": "Please explain the following text in simple, easy-to-understand terms:\n\n{text}",
        "proofread": "Please proofread and correct any grammar, spelling, or punctuation errors. Return only the corrected text:\n\n{text}",
        "expand": "Please expand on the following text with more details and examples:\n\n{text}",
        "simplify": "Please simplify the following text to make it easier to understand. Return only the simplified text:\n\n{text}",
        "formalize": "Please rewrite the following text in a more formal, professional tone. Return only the rewritten text:\n\n{text}",
        "casualize": "Please rewrite the following text in a more casual, friendly tone. Return only the rewritten text:\n\n{text}",
    }

    def __init__(self, config: Optional[PrePandaConfig] = None):
        """Initialize the PrePanda service"""
        self.config = config or PrePandaConfig()
        self.conversation_history: List[Message] = []

        # Try to load API key from environment
        if not self.config.api_key:
            self.config.api_key = os.environ.get("PREPANDA_API_KEY", "")
            if not self.config.api_key:
                self.config.api_key = os.environ.get("VENICE_API_KEY", "")

    def set_api_key(self, api_key: str) -> None:
        """Set the API key"""
        self.config.api_key = api_key

    def clear_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []

    def _call_api(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> str:
        """
        Call the Venice.ai API

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (defaults to config.model_ask)
            max_tokens: Maximum tokens (defaults to config.max_tokens_ask)
            temperature: Temperature (defaults to config.temperature)

        Returns:
            Generated text response
        """
        if not self.config.api_key:
            raise ValueError("API key not configured. Please set VENICE_API_KEY environment variable.")

        url = f"{self.config.api_url}/chat/completions"

        payload = {
            "model": model or self.config.model_ask,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens_ask,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
        }

        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""
            raise RuntimeError(f"API error ({e.code}): {error_body}")
        except urllib.error.URLError as e:
            raise RuntimeError(f"Network error: {e.reason}")

    def ask(self, question: str, context: Optional[str] = None) -> str:
        """
        Ask a question with optional document context

        Args:
            question: User's question
            context: Optional document context (selected text)

        Returns:
            AI response
        """
        # Build messages
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Add context if provided
        if context:
            context_msg = f"Document context:\n{context[:4000]}"  # Limit context size
            messages.append({"role": "user", "content": context_msg})
            messages.append({"role": "assistant", "content": "I understand the context. How can I help you with this text?"})

        # Add conversation history (last 6 messages)
        for msg in self.conversation_history[-6:]:
            messages.append({"role": msg.role, "content": msg.content})

        # Add current question
        messages.append({"role": "user", "content": question})

        # Call API
        response = self._call_api(messages)

        # Update history
        self.conversation_history.append(Message(role="user", content=question))
        self.conversation_history.append(Message(role="assistant", content=response))

        return response

    def perform_action(
        self,
        action: str,
        text: str,
        language: str = "English",
    ) -> str:
        """
        Perform a quick action on text

        Args:
            action: Action to perform (summarize, improve, translate, etc.)
            text: Text to process
            language: Target language for translation

        Returns:
            Processed text
        """
        if action not in self.PROMPTS:
            return self.ask(f"Please {action} the following text:\n\n{text}")

        prompt_template = self.PROMPTS[action]
        prompt = prompt_template.format(text=text, language=language)

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        return self._call_api(messages)

    def summarize(self, text: str) -> str:
        """Summarize text"""
        return self.perform_action("summarize", text)

    def improve(self, text: str) -> str:
        """Improve text quality"""
        return self.perform_action("improve", text)

    def translate(self, text: str, language: str = "English") -> str:
        """Translate text"""
        return self.perform_action("translate", text, language)

    def explain(self, text: str) -> str:
        """Explain text in simple terms"""
        return self.perform_action("explain", text)

    def proofread(self, text: str) -> str:
        """Proofread and correct text"""
        return self.perform_action("proofread", text)

    def expand(self, text: str) -> str:
        """Expand text with more details"""
        return self.perform_action("expand", text)

    def simplify(self, text: str) -> str:
        """Simplify text"""
        return self.perform_action("simplify", text)

    def formalize(self, text: str) -> str:
        """Make text more formal"""
        return self.perform_action("formalize", text)

    def casualize(self, text: str) -> str:
        """Make text more casual"""
        return self.perform_action("casualize", text)

    def generate_smart_result(self, query: str, search_results: List[Dict[str, str]]) -> str:
        """
        Generate a smart result summary from search results
        Similar to PreGPT's smart result feature

        Args:
            query: Search query
            search_results: List of search result dicts with 'title' and 'description'

        Returns:
            Generated summary
        """
        # Format search results
        results_text = "\n".join([
            f"{i+1}. {r.get('title', 'Untitled')} - {r.get('description', '')[:150]}"
            for i, r in enumerate(search_results[:7])
        ])

        prompt = f"""Task: Provide a concise Smart Result for the query: "{query}"

Search Results:
{results_text}

Based on the search results above, provide a helpful summary that answers the query. Keep it clean and concise (max 50 words)."""

        messages = [
            {"role": "system", "content": "You are Presearch Smart Results (PreGPT). Provide concise, accurate summaries."},
            {"role": "user", "content": prompt},
        ]

        return self._call_api(
            messages,
            model=self.config.model_smart,
            max_tokens=self.config.max_tokens,
            temperature=0.5,
        )


# LibreOffice UNO integration
def create_prepanda_service():
    """Factory function for creating PrePanda service instance"""
    return PrePandaService()


# CLI interface for testing
if __name__ == "__main__":
    import sys

    service = PrePandaService()

    if len(sys.argv) < 2:
        print("Usage: python prepanda_service.py <action> [text]")
        print("Actions: ask, summarize, improve, translate, explain, proofread")
        sys.exit(1)

    action = sys.argv[1]
    text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None

    if not text:
        print("Enter text (Ctrl+D to end):")
        text = sys.stdin.read().strip()

    try:
        if action == "ask":
            result = service.ask(text)
        else:
            result = service.perform_action(action, text)
        print(result)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
