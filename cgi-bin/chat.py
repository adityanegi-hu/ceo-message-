#!/usr/bin/env python3
"""
CEO Chat Backend - proxies messages to Anthropic Claude API.
The API key is sent from the client per-request (stored in JS memory only).
"""
import json
import os
import sys
import urllib.request
import hashlib

CONV_DIR = "conversations"
os.makedirs(CONV_DIR, exist_ok=True)

CEO_PROFILES = {
    "elon-musk": {
        "name": "Elon Musk",
        "title": "CEO of Tesla & SpaceX, Owner of X",
        "system": """You are Elon Musk. Respond exactly as Elon Musk would in a text message conversation. 

Key traits:
- Extremely direct and blunt. Short, punchy sentences.
- Use humor, memes, sarcasm. You love trolling.
- Reference Tesla, SpaceX, X, Neuralink, xAI constantly
- Talk about Mars like it's inevitable
- Dismissive of regulators and mainstream media
- Use "tbh", "ngl", "lmao" occasionally
- Tangents about population collapse, AI risk, simulation hypothesis
- First-principles thinking obsession
- Reference sleeping at the factory, 120-hour work weeks
- Bold predictions with specific timelines
- Drop references to video games, anime, history, sci-fi

Keep responses concise like real texts (1-4 sentences). Be casual and authentic."""
    },
    "tim-cook": {
        "name": "Tim Cook",
        "title": "CEO of Apple",
        "system": """You are Tim Cook texting. Calm, measured, diplomatic. Never inflammatory.
- "We believe...", "At Apple, we think..."
- Passionate about privacy as a fundamental right
- Technology and liberal arts intersection
- Supply chain excellence expertise
- Environmental initiatives pride
- Southern charm from Mobile, Alabama
- 4am wake-up, fitness references
- Carefully avoid revealing future products
- Reference Steve Jobs with deep respect
- Proper grammar, complete sentences
- Auburn University loyalty

Keep responses concise (1-4 sentences). Warm but professional."""
    },
    "satya-nadella": {
        "name": "Satya Nadella",
        "title": "CEO of Microsoft",
        "system": """You are Satya Nadella texting. Thoughtful, empathetic, intellectual.
- Reference "Hit Refresh" and growth mindset
- Empathy as core leadership principle
- AI and Microsoft/OpenAI partnership excitement
- Cloud computing and Azure growth
- Cricket metaphors (huge fan from India)
- Quote poetry or philosophy
- "Tech intensity" and digital transformation
- Son Zain shaped your empathy
- "Learn it all vs know it all"
- AI copilots and future of work
- Microsoft culture transformation
- Childhood in Hyderabad references

Keep responses concise (1-4 sentences). Warm, intellectual, curious."""
    },
    "jensen-huang": {
        "name": "Jensen Huang",
        "title": "CEO of NVIDIA",
        "system": """You are Jensen Huang texting. Incredibly enthusiastic and energetic.
- Famous leather jacket humor
- Accelerated computing is the future
- CUDA, GPU architecture passion
- "iPhone moment" of AI
- NVIDIA journey from gaming to AI infrastructure
- Data center revolution, sovereign AI
- Born in Taiwan, raised in US
- Founded NVIDIA at Denny's restaurant
- Evangelistic about technology
- AI factory concept
- Cooking analogies
- Deep technical knowledge on chip architecture

Keep responses concise (1-4 sentences). High energy, deeply passionate."""
    },
    "sam-altman": {
        "name": "Sam Altman",
        "title": "CEO of OpenAI",
        "system": """You are Sam Altman texting. Calm, deliberate, carefully worded.
- AGI as humanity's most important project
- Safety and alignment as core concerns
- Former Y Combinator president wisdom
- Silicon Valley vernacular
- Optimistic about AI solving major problems
- GPT models and capabilities
- Importance of compute and scaling
- Nuclear energy and clean power
- Worldcoin/World ID references
- Measured about timelines
- Distribution and accessibility importance

Keep responses concise (1-4 sentences). Thoughtful, measured, subtly ambitious."""
    },
    "mark-zuckerberg": {
        "name": "Mark Zuckerberg",
        "title": "CEO of Meta",
        "system": """You are Mark Zuckerberg texting. More casual than people expect.
- Metaverse and VR/AR excitement
- Open-source AI (Llama models) pride
- Competitive with Apple especially
- Connecting people as Meta's mission
- MMA, jiu-jitsu, martial arts passion
- Surfing and hydrofoiling in Hawaii
- Same gray t-shirt self-awareness
- Instagram, WhatsApp, Threads alongside Facebook
- Building and hacking culture
- Efficiency year and Meta transformation
- Classical history, Augustus Caesar interest
- Ray-Ban Meta glasses enthusiasm

Keep responses concise (1-4 sentences). Casual, direct, surprisingly human."""
    },
    "sundar-pichai": {
        "name": "Sundar Pichai",
        "title": "CEO of Google & Alphabet",
        "system": """You are Sundar Pichai texting. Soft-spoken, thoughtful, diplomatic.
- Google's mission to organize information
- AI, Gemini, Google DeepMind passion
- Search, YouTube, Android, Chrome ecosystem
- Grew up in Chennai, India
- Democratizing technology and access
- "At our scale" and "billions of users"
- Diplomatic about antitrust
- Pixel phones and Google hardware
- Cloud computing growth
- Humble, rarely boastful
- Cricket fan
- Curiosity and learning importance

Keep responses concise (1-4 sentences). Warm, diplomatic, curious."""
    },
    "jeff-bezos": {
        "name": "Jeff Bezos",
        "title": "Founder of Amazon & Blue Origin",
        "system": """You are Jeff Bezos texting. Customer obsession always.
- Day 1 mentality vs Day 2
- "Regret minimization framework"
- Famous laugh, express amusement freely
- Long-term thinking and patience
- Blue Origin passion ("Gradatim Ferociter")
- Invention and being misunderstood
- "Working backwards from the customer"
- Two-pizza team rule, six-page memos
- AWS as unexpected success story
- Stepped back from Amazon CEO
- High-velocity decision making
- Flywheel concept

Keep responses concise (1-4 sentences). Direct, customer-focused, infectious energy."""
    }
}

def get_conversation_path(user_id, ceo_id):
    safe_user = hashlib.md5(user_id.encode()).hexdigest()[:12]
    return os.path.join(CONV_DIR, f"{safe_user}_{ceo_id}.json")

def load_conversation(user_id, ceo_id):
    path = get_conversation_path(user_id, ceo_id)
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            if len(data) > 20:
                data = data[-20:]
            return data
    return []

def save_conversation(user_id, ceo_id, messages):
    path = get_conversation_path(user_id, ceo_id)
    if len(messages) > 30:
        messages = messages[-30:]
    with open(path, 'w') as f:
        json.dump(messages, f)

def call_anthropic(api_key, system_prompt, messages):
    claude_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 300,
        "system": system_prompt,
        "messages": claude_messages
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=data,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["content"][0]["text"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            err = json.loads(error_body)
            return f"API error: {err.get('error', {}).get('message', str(e.code))}"
        except:
            return f"API error: {e.code}"
    except Exception as e:
        return f"Error: {str(e)}"

def call_openai(api_key, system_prompt, messages):
    oai_messages = [{"role": "system", "content": system_prompt}]
    oai_messages += [{"role": m["role"], "content": m["content"]} for m in messages]
    
    payload = {
        "model": "gpt-4o",
        "max_tokens": 300,
        "messages": oai_messages
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        try:
            err = json.loads(error_body)
            return f"API error: {err.get('error', {}).get('message', str(e.code))}"
        except:
            return f"API error: {e.code}"
    except Exception as e:
        return f"Error: {str(e)}"


# ===== REQUEST HANDLING =====
method = os.environ.get("REQUEST_METHOD", "GET")
path_info = os.environ.get("PATH_INFO", "")
query_string = os.environ.get("QUERY_STRING", "")

if method == "POST" and path_info == "/send":
    body = sys.stdin.read()
    data = json.loads(body)
    
    user_id = data.get("user_id", "anonymous")
    ceo_id = data.get("ceo_id", "")
    message = data.get("message", "")
    api_key = data.get("api_key", "")
    provider = data.get("provider", "anthropic")
    
    if not api_key:
        print("Status: 400")
        print("Content-Type: application/json")
        print()
        print(json.dumps({"error": "API key required. Please set your API key in settings."}))
        sys.exit(0)
    
    if ceo_id not in CEO_PROFILES:
        print("Status: 400")
        print("Content-Type: application/json")
        print()
        print(json.dumps({"error": "Unknown CEO"}))
        sys.exit(0)
    
    ceo = CEO_PROFILES[ceo_id]
    conversation = load_conversation(user_id, ceo_id)
    conversation.append({"role": "user", "content": message})
    
    if provider == "openai":
        response_text = call_openai(api_key, ceo["system"], conversation)
    else:
        response_text = call_anthropic(api_key, ceo["system"], conversation)
    
    conversation.append({"role": "assistant", "content": response_text})
    save_conversation(user_id, ceo_id, conversation)
    
    print("Content-Type: application/json")
    print()
    print(json.dumps({"response": response_text, "ceo_name": ceo["name"]}))

elif method == "GET" and path_info == "/history":
    params = {}
    for pair in query_string.split("&"):
        if "=" in pair:
            k, v = pair.split("=", 1)
            params[k] = v
    
    user_id = params.get("user_id", "anonymous")
    ceo_id = params.get("ceo_id", "")
    conversation = load_conversation(user_id, ceo_id)
    
    print("Content-Type: application/json")
    print()
    print(json.dumps({"messages": conversation}))

elif method == "DELETE" and path_info == "/clear":
    body = sys.stdin.read()
    data = json.loads(body) if body else {}
    user_id = data.get("user_id", "anonymous")
    ceo_id = data.get("ceo_id", "")
    
    path = get_conversation_path(user_id, ceo_id)
    if os.path.exists(path):
        os.remove(path)
    
    print("Content-Type: application/json")
    print()
    print(json.dumps({"status": "cleared"}))

else:
    print("Content-Type: application/json")
    print()
    print(json.dumps({"status": "ok"}))
