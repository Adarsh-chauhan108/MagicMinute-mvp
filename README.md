# ✨ MagicMinute — AI Email Assistant  
🧠 Advanced Email Agent · Retro-Future Interface · Powered by GPT-4 Turbo

MagicMinute is an intelligent, prompt-based Gmail assistant that helps users write, schedule, and auto-respond to emails. It features a futuristic interface, AI-generated drafts, scheduled delivery, and a smart auto-reply system.

---

## 🚀 Features

### ✍️ 1. Draft-First Email Workflow
Use natural prompts like:
> `send a mail to chauhanadarsh101@gmail.com about a basic flask app starter code`

MagicMinute generates the draft using GPT-4.  
You can then:
- ✅ **Send instantly** → `send it`
- ⏰ **Schedule it** → `schedule it at 1:30pm`

---

### 🤖 2. AI Auto-Reply System

#### 🔁 Static Replies  
Set a fixed message like:  
> “I’m currently unavailable. I’ll respond soon.”

#### 🧠 Smart AI Replies 
If enabled, MagicMinute understands incoming emails and replies contextually.

Example:  
Email: *“Can you share the prime number code in Python?”*  
MagicMinute reply: *“Sure! Here’s a Python snippet for that...”*

---

## 💡 Example Prompts

| 🎯 Task                    | 🧠 Prompt                                  |
|----------------------------|-------------------------------------------|
| Compose an email           | `email Sarah about project delay`         |
| Send generated draft       | `send it`                                 |
| Schedule for later         | `schedule it at 9:45am`                   |
| Enable static reply        | Toggle in sidebar                         |
| Enable smart auto-replies  | Toggle in sidebar                         |

---

## 🛠️ How to Run

### 1. Clone & install
```bash
git clone https://github.com/your-username/magicminute-mvp
cd magicminute-mvp
pip install -r requirements.txt
```

### 2. Launch the App
```bash
streamlit run app/ui.py
```

### 3. Authenticate Gmail
- Place your `credentials.json` inside the `app/` folder  
- A browser window will open on first launch to authenticate your Google account  
- Token is saved as `app/token.json` (automatically)

---

### 🔐 Environment Setup

Create a `.env` file in the root folder and add your OpenAI key:

```env
OPENAI_API_KEY=your-api-key-here
```
---

## 🎯 Use Cases

- 🧳 Professionals setting auto-replies during time off  
- ✉️ Founders drafting and scheduling outreach emails  
- 📚 Students automating email workflows and coding support  
- 🧠 Anyone who wants a fun, natural email experience

---

## 🧭 Roadmap (Post-MVP)

- ✅ Smart email drafting & scheduling (done)  
- 🔜 Contact and signature memory  
- 🔜 Metadata export as ERC-3525 profile  
- 🔜 Multi-agent inbox delegation  
- 🔜 Voice or SMS-based AI input  

---

## Demo Link
- https://drive.google.com/file/d/1SRtuh4AUs1mKoyuY4-5yxMg9P5hEgTK2/view?usp=drivesdk

## 📄 License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2025 Adarsh Singh Chauhan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🧑‍🚀 Built by

**Adarsh Singh Chauhan**  
Dreaming of a world where AI sits in booths, banks, browsers, and inboxes — empowering humans, not replacing them.