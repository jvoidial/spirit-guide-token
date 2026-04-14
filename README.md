# phb-api
# 🧠 PHB AI Operating System (PHB OS)

A modular, event-driven AI runtime system built on FastAPI with a plugin architecture, persistent memory layer, and hardened execution core.


"git clone https://github.com/jvoidial/phb-api.git
cd phb-api"


"cat << 'EOF' > install.sh
#!/bin/bash

echo "🧠 PHB AI OS INSTALLER STARTING..."

if [ ! -d "phb-api" ]; then
  git clone https://github.com/jvoidial/phb-api.git
fi

cd phb-api || exit 1

mkdir -p phb/{cognition,memory,bridge,supervisor,world_model,sync}

touch phb/__init__.py
touch phb/cognition/__init__.py
touch phb/memory/__init__.py
touch phb/bridge/__init__.py
touch phb/supervisor/__init__.py

export PYTHONPATH=$PWD

if [ -f requirements.txt ]; then
  pip install -r requirements.txt
fi

pkill -f uvicorn || true

echo "🚀 Starting PHB OS..."
bash phb-api/run.sh &

sleep 3

curl -s http://localhost:8000/ || echo "⚠ Server starting..."

echo "🟢 INSTALL COMPLETE"
echo "👉 http://localhost:8000"
EOF"


"chmod +x install.sh
bash install.sh"

Current Stable Version: **v3.2.1 (Stability Hardening)**

---

## ⚙️ Overview

PHB OS is a lightweight AI operating system architecture designed to behave like a controlled runtime kernel rather than a traditional chatbot.

It provides:

- 🧠 Persistent user memory layer
- 🔌 Plugin-based tool execution system
- ⚡ Event-driven message routing
- 🛡 Safe execution and crash isolation
- 📦 Modular AI system design (kernel-style architecture)

---

## 🧠 Core Design Principles

### 1. Deterministic Execution
Every input flows through a controlled pipeline:


---

### 2. Plugin Isolation
Plugins are dynamically loaded and safely isolated so that failures do not crash the system.

---

### 3. Memory Persistence
User interactions are stored in a lightweight persistent memory layer for contextual continuity.

---

### 4. Event-Driven Architecture
Internal system communication is handled through an event bus model rather than direct coupling.

---

## 🚀 Features

### 🧠 Memory System
- Stores per-user message history
- Provides interaction count tracking
- Thread-safe writes (v3.2.1 hardened)

---

### 🔌 Plugin System
- Auto-loads Python plugins from `/phb/plugins`
- Safe execution with exception isolation
- Returns first valid plugin response

---

### ⚡ Event Bus
- Decoupled message routing system
- Safe handler execution (no silent failures)
- Extensible event architecture



### 🛡 Stability Layer (v3.2.1)
- Plugin crash isolation
- Memory consistency locks
- Hardened event handling
- Improved runtime safety

---
cat << 'EOF' > README.md

# 🧠 PHB AI OPERATING SYSTEM (PHB OS)

A modular **cognitive operating system for AI reasoning, memory, and autonomous execution** built on FastAPI.

Current Version: **v4.x Cognitive Runtime Series**

---

## ⚙️ Overview

PHB OS is not a chatbot.

It is a **cognitive runtime kernel** designed to behave like an AI operating system with:

- 🧠 Persistent memory layer  
- 🤖 Long-horizon reasoning engine  
- 🌍 World model prediction system  
- 🔗 Bridge routing architecture  
- 🛠 Supervisor + runtime stability layer  
- 🔄 Auto-healing execution system  

It transforms input into **structured thought, memory, planning, and execution cycles**.

---

## 🧠 What PHB Actually Does

When you send input like:

```text
"hello brain"
