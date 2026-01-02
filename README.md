# AI Personal Assistant 

A multi-agent AI system with a web interface where you can chat as well as speak with a coordinator agent that delegates tasks to specialized subagents.


## Features

✓ **Web Interface** - Natural conversation with your AI assistant
✓ **TTS/STT** - You can talk to your assistant using your microphone and the assistant can speak responses back to you.
✓ **RAG Agent** - Natural conversation with your AI assistant
✓ **Coordinator Agent** - Understands requests and delegates to subagents
✓ **Email Management** - Summarize, read, and send emails
✓ **Calendar Management** - Schedule meetings and check availability
✓ **Smart Reminders** - Get notified about upcoming events
✓ **Real-time Status** - See unread emails and upcoming events
✓ **Autonomous Auto-Reply** - Automatically responds to resume/profile requests

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Get Google Cloud credentials:**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project
   - Enable Gmail API and Google Calendar API
   - Create OAuth 2.0 credentials
   - Add redirect URI: `http://localhost:8080/`
   - Download as `credentials.json`

3. **Get Google Gemini API key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key

4. **Configure environment:**
   - Add your API key  to `.env`
   ```
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

5. **Run the web app:**
```bash
python app.py
```

6. **Open browser:**
   - Go to: http://localhost:5000

## Usage Examples

Chat with your agent:

- "Summarize my emails"
- "Send an email to john@example.com saying hello"
- "Schedule a meeting tomorrow at 2pm"
- "What are my upcoming meetings?"
- "Check my calendar for next week"

The coordinator will:
1. Understand your request
2. Delegate to the appropriate subagent
3. Execute the task
4. Report back with results

## How It Works

1. User sends a message in the chat
2. **Coordinator Agent** analyzes the request using Gemini
3. Coordinator delegates to appropriate subagent:
   - **EmailAgent** for email tasks
   - **CalendarAgent** for scheduling
   - **ReminderAgent** for notifications
4. Subagent executes the task
5. Coordinator returns completion message

#  Autonomous Auto-Reply Workflow

Voice-triggered replies

Auto-replies based on voice (voice → STT → classify → reply)

RAG-based personalized responses using your résumé or portfolio

Transformer-based tone control

## Auto-Reply Flow (Fully Autonomous)

```
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Email Arrives                                      │
│  ┌────────────────────────────────────────────────┐         │
│  │ From: recruiter@company.com                    │         │
│  │ Subject: "Can you share your resume?"          │         │
│  │ Body: "We're hiring for a Senior Dev role..."  │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Coordinator Runs (Every 5 minutes)                 │
│  • Fetches unread emails                                    │
|  • RAG agent gets the details                               |
│  • Passes to AutoReplyAgent                                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: AutoReplyAgent Analyzes                            │
│  ┌────────────────────────────────────────────────┐         │
│  │ ✓ Check exclusions (spam, newsletters)         │         │
│  │ ✓ Scan for keywords: "resume", "skills"        │         │
│  │ ✓ Classify type: RESUME REQUEST                │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Load User Profile                                  │
│  ┌────────────────────────────────────────────────┐         │
│  │ • Personal info                                │         │
│  │ • Professional summary                         │         │
│  │ • Technical skills                             │         │
│  │ • Experience                                   │         │
│  │ • Availability                                 │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: AI Generates Personalized Reply                    │
│  ┌────────────────────────────────────────────────┐         │
│  │ Using: Google Gemini                           │         │
│  │                                                │         │
│  │ Prompt includes:                               │         │
│  │ • Original email context                       │         │
│  │ • User profile data                            │         │
│  │ • Tone settings (professional/friendly)        │         │
│  │ • Max word count                               │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: Send Reply With RAG specified                      │
│  ┌────────────────────────────────────────────────┐         │
│  │ To: recruiter@company.com                      │         │
│  │ Subject: Re: Can you share your resume?        │         │
│  │ Thread: Same email thread                      │         │
│  │                                                │         │
│  │ Body: "Thank you for reaching out!             │         │
│  │        I'd be happy to share my background..." │         │
│  │        [Personalized content from profile]     │         │
│  └────────────────────────────────────────────────┘         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 7: Mark as Read & Log                                 │
│  ✓ Email marked as read                                     │
│  ✓ Action logged to console                                 │
│  ✓ Ready for next email                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                     DONE! (No manual action needed)
```

## Response Generation

```
┌─────────────────────────────────────────────────────────┐
│  Input to AI                                            │
│  ┌───────────────────────────────────────────────────┐  │
│  │ 1. Original Email                                 │  │
│  │    • Sender                                       │  │
│  │    • Subject                                      │  │
│  │    • Body                                         │  │
│  │                                                   │  │
│  │ 2. User Profile (filtered by type)                │  │
│  │    • Resume: Full background                      │  │
│  │    • Skills: Technical expertise                  │  │
│  │    • Profile: General overview                    │  │
│  │    • Availability: Job preferences                │  │
│  │                                                   │  │
│  │ 3. Configuration                                  │  │
│  │    • Tone: professional/friendly                  │  │
│  │    • Max words: 300                               │  │
│  │    • Signature: "Best regards"                    │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Google Gemini                                          │
│  • Understands context                                  │
│  • Generates natural language                           │
│  • Maintains professional tone                          │
│  • Includes relevant details                            │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│  Output: Personalized Email                             │
│  ┌───────────────────────────────────────────────────┐  │
│  │ • Greeting                                        │  │
│  │ • Thank you message                               │  │
│  │ • Relevant information                            │  │
│  │ • Key highlights                                  │  │
│  │ • Contact details                                 │  │
│  │ • Professional closing                            │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```



**Result**: Fully autonomous email handling with zero manual intervention along with RAG integration ! 


## Automated Mode

You can also run the automated background agent:
```bash
python main.py
```

This runs every 5 minutes to automatically process emails and send reminders.

##  Autonomous Auto-Reply Feature

The **AutoReplyAgent** is a fully autonomous agent with RAG that monitors your inbox and automatically responds to resume, technical skills, and profile-related inquiries.

### How It Works

1. **Automatic Detection**: Scans incoming emails for keywords like:
   - Resume/CV requests
   - Technical skills inquiries
   - Profile information requests
   - Job availability questions

2. **Intelligent Response**: Uses AI and RAG to generate personalized, professional replies based on your `user_profile.json` 

3. **Zero Manual Intervention**: Completely autonomous - no approval needed!

### Setup Your Profile
Add your documents to `rag_data`

Edit `user_profile.json` with your information:

```json
{
  "personal_info": {
    "name": "Your Name",
    "email": "your.email@example.com",
    "linkedin": "https://linkedin.com/in/yourprofile",
    "github": "https://github.com/yourusername"
  },
  "professional_summary": "Your professional summary...",
  "technical_skills": {
    "programming_languages": ["Python", "JavaScript"],
    "frameworks": ["React", "Django"]
  },
  "experience": [...],
  "availability": {
    "status": "open_to_opportunities",
    "preferred_roles": ["Senior Developer"]
  }
}
```

### Test Auto-Reply

Run the test script to see it in action:
```bash
python test_auto_reply.py
```

### What Happens Automatically

1. Email arrives asking about your resume
2. AutoReplyAgent detects the request type
3. Generates personalized response using your profile
4. Sends reply in the same email thread
5. Marks email as read
6. No manual action required!

### Example Auto-Reply

**Incoming Email:**
> "Hi, I'm a recruiter at TechCorp. Could you share your resume and technical skills?"

**Automatic Response:**
> "Thank you for reaching out! I'd be happy to share my background.
> 
> I'm a Senior Software Engineer with 5+ years of experience in full-stack development. My technical expertise includes Python, JavaScript, React, Django, and cloud platforms like AWS and Google Cloud.
> 
> [Detailed experience and skills from your profile]
> 
> I'm currently open to opportunities in Senior Developer and Tech Lead roles. Feel free to reach out if you'd like to discuss further!
> 
> Best regards,
> [Your Name]"

### Disable Auto-Reply

To disable autonomous replies, simply comment out the auto-reply section in `coordinator.py`:

```python
# Step 1.5: Auto-reply (comment out to disable)
# auto_reply_result = self.auto_reply_agent.process({...})
```

##  Quick Stats

- **Setup Time**: ~15 minutes
- **Response Time**: 5-10 seconds per email
- **Manual Intervention**: ZERO 
- **Accuracy**: High (AI + keyword matching)
- **Customizable**: 100% configurable

# Autonomous-Agentic-System
# myagent
