# Hermes AI Assistant

อัจฉริยะผู้ช่วย AI ที่สร้างบนพื้นฐาน Hermes TUI

## โครงสร้างโปรเจค

```
hermes-ai-assistant/
├── pyproject.toml          # Project configuration
├── src/
│   ├── main.py             # Entry point
│   ├── core/
│   │   └── assistant.py    # Main AI orchestrator
│   ├── intelligence/
│   │   ├── intent_analyzer.py   # Intent classification
│   │   ├── context_manager.py   # Context management
│   │   ├── task_orchestrator.py # Multi-step task planning
│   │   └── skill_router.py      # Skill discovery & routing
│   ├── agents/
│   │   ├── multi_agent.py    # Multi-agent orchestrator
│   │   ├── research_agent.py # Research agent
│   │   └── code_agent.py     # Code generation/review
│   ├── memory/
│   │   └── memory_manager.py # Persistent memory + learning
│   ├── integrations/
│   │   └── hub.py           # Web search, tools, hooks
│   └── ui/
│       └── tui_integration.py # TUI bridge
├── config/                  # Configuration files
├── tests/
│   └── test_assistant.py   # Test suite
└── data/                    # Runtime data
```

## คุณสมบัติ

- **Intent Analyzer** — วิเคราะห์เจตนาผู้ใช้ (ภาษาไทย/อังกฤษ)
- **Context Manager** — จัดการบริบทการสนทนาอัจฉริยะ
- **Task Orchestrator** — วางแผนและรันงานหลายขั้นตอน
- **Skill Router** — ค้นหาและเรียกใช้ทักษะ Hermes
- **Multi-Agent** — ประสานงานตัวแทนหลายตัวขนาน
- **Research Agent** — ค้นคว้าข้อมูล
- **Code Agent** — สร้าง/ทบทวน/ดีบักโค้ด
- **Memory Manager** — จำและเรียนรู้จากการโต้ตอบ
- **Integration Hub** — เชื่อมต่อเว็บเซิร์ชและเครื่องมือ
- **TUI Integration** — เชื่อมต่อกับ Hermes TUI

## การใช้งาน

```bash
# รันโปรแกรม
python src/main.py

# รัน tests
pytest tests/
```

## ตัวอย่างการใช้งาน

```
👤 You: ค้นหา Python tutorial
🤖 AI [search] (confidence: 80%)
   🎯 Skill: web_search
   Search results for 'Python tutorial': 0 found

👤 You: เขียนโค้ด Python
🤖 AI [code] (confidence: 70%)
   Generated code (5 lines, score: 100)
```
