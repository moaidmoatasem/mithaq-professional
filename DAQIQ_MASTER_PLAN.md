# mithaq Security Framework - Master Plan

## Project Overview
**Name:** mithaq (دقيق) - "Precision" in Arabic  
**Mission:** AI-powered mobile security auditing for MENA enterprises  
**Timeline:** 30 weeks (Apr 26 - Nov 30, 2026)  
**Budget:** $0 (free tier APIs only)

## Architecture Summary

### The Four Components
1. **Al-Muhandis** (المهندس) - Cloud Strategist (Groq/Gemini)
2. **Al-Munafeedh** (المنفذ) - Local Executor (Ollama)
3. **Al-Markaz** (المركز) - Orchestrator (Python)
4. **Al-Burhan** (البرهان) - Proof Generator (PoC validation)

## Zero-Trust Model
Cloud receives only abstract breadcrumbs. All sensitive data stays local.

## Phase 0: Foundation (Week 1)
- Pydantic schemas with prompt injection defense
- Sanitizer with HMAC signing
- 80% test coverage requirement

See TODO.md for complete roadmap.

