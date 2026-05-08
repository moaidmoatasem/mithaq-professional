# cherenkov Development TODO

## Phase 0: Foundation (Week 1) - IN PROGRESS
- [x] Repository setup
- [x] Agent rules configuration  
- [ ] CloudInstruction Pydantic schema
- [ ] AblationSanitizer with HMAC
- [ ] Test suite (6/6 tests passing)

## Phase 1: Multi-Provider Orchestration (Week 2-8)
- [ ] HTTP client for Groq/Gemini
- [ ] Fallback logic (Groq → Gemini → Ollama)
- [ ] Circuit breaker (3-strike rule)
- [ ] Rate limit enforcer (30 RPM Groq, 15 RPM Gemini)
- [ ] Integration tests

## Phase 2: Tool Integration (Week 9-20)
- [ ] APKTool wrapper
- [ ] Androguard integration
- [ ] Frida hook generator
- [ ] Drozer PoC executor

## Phase 3: Tokamak Validation (Week 21-28)
- [ ] PoC runner (safe, non-destructive)
- [ ] Evidence verification
- [ ] False positive elimination

## Phase 4: Security Hardening (Week 29-35)
- [ ] Supply chain audit (pip-audit)
- [ ] SBOM generation
- [ ] Penetration testing

## Phase 5: Enterprise Readiness (Week 36-41)
- [ ] PyQt6 UI
- [ ] PDF reporter
- [ ] SARIF exporter
- [ ] DIVA benchmark (target: <8 min, >95% precision)

## Current Sprint (Week 1 - Today: Apr 26, 2026)
**Focus:** Phase 0 foundation  
**Next task:** CloudInstruction Pydantic schema  
**Assigned to:** Roo Code (Builder - Gemini 2.5 Flash)  
**Branch:** feature/pydantic-gates  
**Target completion:** Today, 6:00 PM EEST

