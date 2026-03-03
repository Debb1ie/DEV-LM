# DevLog

A developer-focused AI knowledge base — like NotebookLM, built for engineers.

![DevLog](https://img.shields.io/badge/version-1.0.0-7c6af7?style=flat-square) ![HTML](https://img.shields.io/badge/stack-HTML%20%2F%20CSS%20%2F%20JS-353555?style=flat-square) ![Claude](https://img.shields.io/badge/AI-Claude%20Sonnet%204-7c6af7?style=flat-square)

---

## What it is

DevLog lets you build notebooks around your codebases, documentation, and technical sources, then chat with them using AI. Ask questions, get code explanations, compare approaches, and save insights — all in one place.

---

## Features

**3-column layout**
- **Sources** — add files, URLs, GitHub repos, npm/PyPI packages, API docs, or pasted code
- **Chat** — AI-powered Q&A grounded in your sources, with code highlighting and inline citations
- **Studio** — generate Audio Overviews, Mind Maps, Flashcards, Quizzes, Slide Decks, Reports, and more from your notebook

**Developer-first details**
- `JetBrains Mono` for all source filenames and code
- Syntax highlighting in chat responses (keywords, strings, comments)
- Source count pill in the chat input showing how many sources are active
- Select/deselect individual sources to scope your queries
- Save any AI response directly to notes
- Create notebooks by category: Backend, Frontend, DevOps, Research, Architecture, Mobile

---

## Setup

This is a single HTML file with no build step required.

```bash
git clone https://github.com/yourname/devlog
cd devlog
open devlog.html
```

> The AI chat requires access to the Anthropic API. When running inside Claude.ai artifacts, the API key is handled automatically. For self-hosting, see the section below.

---

## Self-hosting with your own API key

The chat calls `https://api.anthropic.com/v1/messages` directly from the browser. To use this outside of Claude.ai, you will need to either:

1. Add a proxy server that injects your API key, or
2. Modify the fetch call in the script to include your key:

```js
headers: {
  'Content-Type': 'application/json',
  'x-api-key': 'YOUR_API_KEY',
  'anthropic-version': '2023-06-01'
}
```

> Do not expose your API key in client-side code in production. Use a backend proxy.

---

## Customizing the notebook

To change the default notebook content, edit these values near the bottom of the `<script>` block:

```js
// Default sources
const sources = [
  { id: 1, type: 'file', name: 'server.ts — Express setup', sel: true },
  { id: 2, type: 'file', name: 'cluster.js — Worker threads', sel: true },
  { id: 3, type: 'link', name: 'nodejs.org/en/docs', sel: true },
];
```

To change the AI system prompt and notebook context, find `const sys = ...` inside `getResponse()` and update the sources description to match your actual content.

---

## Model

Uses `claude-sonnet-4-20250514` by default. To switch models, update:

```js
model: 'claude-sonnet-4-20250514'
```

---

## Stack

| Layer | Tech |
|---|---|
| UI | Vanilla HTML / CSS / JS |
| Fonts | Inter (UI), JetBrains Mono (code) |
| Icons | Inline SVG symbols |
| AI | Anthropic Claude API (`/v1/messages`) |
| Build | None — single file |

---

## File structure

```
devlog.html      # Everything — styles, markup, scripts, SVG icons
README.md        # This file
```

---

## License

MIT
