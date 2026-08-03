---
type: LLM Context File
title: LLM Context
description: LLM context file for TokenBel Wiki with securities market data references
---

# LLM Context

Static context file that provides LLM-based tools with repository overview, section descriptions, and navigation information.

## File Overview

File: `static/llms.txt`

**Purpose**: Provide AI agents and LLM tools with structured information about the TokenBel Wiki repository to enable better understanding and assistance.

**Format**: Plain text with structured sections

## Content Structure

The file contains:

### Repository Overview
- Project name and description
- Technology stack (Hugo, Tailwind CSS, Cloudflare)
- Primary purpose and audience

### Sections
- List of all main sections (news, statistics, guides, policies, about)
- Brief description of each section
- Content types and purposes

### Navigation
- Main menu structure
- Section hierarchy
- Important pages and their purposes

### MCP Server Reference
- Reference to Model Context Protocol server
- Available tools and capabilities
- Integration points

## Usage

### For AI Agents

LLM tools can read this file to:
- Understand the repository structure
- Navigate between sections
- Provide context-aware assistance
- Answer questions about the wiki

### For MCP Clients

The file serves as a reference for MCP (Model Context Protocol) servers that need to understand the repository structure.

## Example Content

```
TokenBel Wiki - Russian-language knowledge base for TokenBel

Sections:
- news: Latest updates and announcements
- statistics: Market data and analytics
- guides: User guides and tutorials
- policies: Terms, conditions, and policies
- about: Project information

Navigation:
Main menu: Новости, Статистика, Руководство, Политика, О проекте

MCP Server: Available for repository introspection
```

## Relationships

* [Site Configuration](hugo-config.md) — Hugo configuration that defines sections
* [Content Layer](../content-layer/) — Content organization matching the sections
* [Architecture](../architecture/) — System architecture overview

## Citations

[1] `static/llms.txt` — LLM context file
[2] `hugo.yaml:20-30` — Menu configuration matching sections
[3] `content/` — Content directory structure
[4] `e9dce87` — Commit that added llms.txt
[5] `DESIGN.md` — Visual design contract referenced in llms.txt
