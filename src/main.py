#!/usr/bin/env python3
"""Hermes AI Assistant — Intelligent Assistant built on Hermes TUI."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from core.assistant import AIAssistant
from ui.tui_integration import TUIIntegration


def main():
    """Main entry point."""
    print("🚀 Hermes AI Assistant Initializing...")
    print("=" * 50)

    # Create assistant
    assistant = AIAssistant()
    tui = TUIIntegration(assistant)

    # Register status hook
    def on_status(status, data):
        print(f"[{status}] {data.get('input', '')}")

    tui.register_status_hook(on_status)

    # Show status
    status = assistant.get_status()
    print(f"Skills loaded: {status['skills']}")
    print(f"Memory entries: {status['memory'].get('entries', 0)}")
    print(f"Agents active: {status['agents']['active_agents']}")
    print(f"Integrations: {status['integrations']}")
    print("=" * 50)

    # Interactive loop
    print("\n💬 พิมพ์ข้อความเพื่อเริ่มสนทนา (หรือ 'quit' เพื่อออก)\n")

    session_id = "main-session"

    while True:
        try:
            user_input = input("👤 You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "เลิก"):
            print("👋 Goodbye!")
            break

        # Process through AI
        result = tui.process_input(user_input, session_id)

        # Display response
        print(f"\n🤖 AI [{result['intent']}] (confidence: {result['confidence']:.0%})")
        if result['skill']:
            print(f"   🎯 Skill: {result['skill']}")
        print(f"   {result['output']}")
        if result.get('memories'):
            print(f"   📝 Memories: {', '.join(result['memories'])}")
        print()


if __name__ == "__main__":
    main()
