# CEO Messages

An iMessage-style web app where you can chat with “tech CEO” personas (Elon, Tim, Sam, Satya, etc.) using **Anthropic (Claude)** or **OpenAI (GPT-4o)**.

## Features

- iMessage-inspired UI (light/dark theme toggle)
- Contacts list + search
- Per-contact conversation threads
- “Typing” indicator + time grouping
- Provider switch: **Anthropic** or **OpenAI**
- Chat history persisted server-side (per session + CEO)

## Project structure

- `index.html`: app shell + onboarding + settings modal
- `style.css` / `base.css`: UI styling
- `app.js`: frontend state + UI rendering + API calls
- `cgi-bin/chat.py`: Python CGI backend (send/history/clear) + persona system prompts
- `cgi-bin/conversations/`: created at runtime to store chat JSON files

## Requirements

- **Python 3.10+** (recommended)
- An **API key** from either:
  - Anthropic (Claude)
  - OpenAI (GPT)

## Run locally

### Option A: Run with Python’s built-in CGI server (quickest)

From the project folder:

```bash
py -m http.server 8000 --cgi
```

Then open:

- `http://localhost:8000/`

Notes:

- The frontend calls the backend at `cgi-bin/chat.py` (endpoints: `/send`, `/history`, `/clear`), so you must run the site through a server for chat to work.
- If CGI doesn’t execute on your Windows setup, use Option B.

### Option B: Run under a CGI-capable server (most reliable)

Use a server that supports CGI (for example Apache, IIS with CGI enabled, or WSL + Apache). Configure it to execute:

- `cgi-bin/chat.py`

And serve `index.html` at the site root.

## How it works

- **Frontend**: you pick a provider + paste an API key in onboarding/settings, then chat in the UI.
- **Backend**: `cgi-bin/chat.py` receives the message and forwards it to Anthropic or OpenAI, using a persona “system prompt” per CEO.
- **Storage**: conversations are saved as JSON files in `cgi-bin/conversations/` keyed by a hashed session id + CEO id.

## Privacy / security notes

- The UI claims your API key is “stored in memory only” on the client (not saved to disk by the app).
- The API key is still **sent to your local backend per request**, and the backend uses it to call the provider API.
- **Do not deploy this publicly** as-is. If you host it, implement proper authentication and server-side secrets handling.

## Customization

### Add / change CEOs

- **Contacts list (frontend)**: edit `CEOS` in `app.js`
- **Personas (backend)**: edit `CEO_PROFILES` in `cgi-bin/chat.py` (the `system` prompt is the persona)

### Avatars

`app.js` references images like:

- `./assets/elon-musk.jpg`

Create an `assets/` folder and add matching images, or update the `avatar` paths in `app.js`.

## Troubleshooting

- **I can open the page but sending messages fails**: you’re likely opening `index.html` directly from disk. Run via a server (see “Run locally”).
- **404 /cgi-bin/chat.py**: the server isn’t configured for CGI or you aren’t using a CGI-enabled mode.
- **Provider errors**: verify your key matches the provider and that your account has access.

## Disclaimer

This project is for entertainment and UI/demo purposes. The “CEO” messages are AI-generated roleplay and are not affiliated with real people or companies.

