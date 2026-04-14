# phb-api
# 🧠 PHB AI Operating System (PHB OS)

A modular, event-driven AI runtime system built on FastAPI with a plugin architecture, persistent memory layer, and hardened execution core.

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

---

### 🛡 Stability Layer (v3.2.1)
- Plugin crash isolation
- Memory consistency locks
- Hardened event handling
- Improved runtime safety

---

## 📁 Project Structure
