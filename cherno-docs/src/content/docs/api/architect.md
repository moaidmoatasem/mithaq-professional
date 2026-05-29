---
title: Architect API
description: Security Architect Tier 3 documentation.
---

# Architect API

The Tier 3 Security Architect agent leverages Foundation-Sec-8B to generate an `EngagementPlan` JSON via LiteLLM proxy. It requires target information and optionally frameworks, requirements, and constraints.

## Endpoint

**`POST /api/v1/architect/plan`**

- Generates an engagement plan for a given target.
- Requires standard JWT authentication via bearer token.
- Uses `ArchitectPlanRequest` body schema containing `target`, `framework`, `requirements`, `constraints`, and `threat_context`.

### Graceful Fallback

In scenarios where the internal `LiteLLM` proxy is offline or encounters an error, the endpoint gracefully catches the exception and yields a fallback JSON to maintain API stability without breaking integration downstream.
