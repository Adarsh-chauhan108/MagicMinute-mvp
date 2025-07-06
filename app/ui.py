import streamlit as st
from datetime import datetime
import re
from main import (
    get_gmail_service,
    send_email,
    parse_time,
    schedule_email_background,
    interpret_task_with_llm,
    resolve_email,
    AutoReplyAgent
)

# Futuristic CSS styling
def load_futuristic_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600&display=swap');
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a0a2e 50%, #16213e 100%);
        color: #e0e0ff;
    }
    
    /* Animated neon logo */
    .neon-logo {
        font-family: 'Orbitron', monospace;
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        margin: 20px 0;
        background: linear-gradient(45deg, #ff0080, #00ffff, #ff0080);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: neonGlow 3s ease-in-out infinite alternate,
                   gradientShift 4s ease-in-out infinite;
        text-shadow: 
            0 0 5px #ff0080,
            0 0 10px #ff0080,
            0 0 20px #ff0080,
            0 0 40px #ff0080;
        filter: drop-shadow(0 0 20px #ff008040);
    }
    
    @keyframes neonGlow {
        0% { filter: brightness(1) drop-shadow(0 0 20px #ff008040); }
        100% { filter: brightness(1.3) drop-shadow(0 0 30px #00ffff60); }
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .subtitle {
        text-align: center;
        font-family: 'Rajdhani', sans-serif;
        font-size: 1.2rem;
        color: #00ffff;
        margin-bottom: 30px;
        text-shadow: 0 0 10px #00ffff40;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #0f0f23 0%, #1a1a3a 100%);
        border-right: 2px solid #00ffff40;
        box-shadow: 5px 0 20px rgba(0, 255, 255, 0.1);
    }
    
    /* Chat messages styling */
    .stChatMessage {
        background: linear-gradient(135deg, #1a1a3a 0%, #2a2a4a 100%);
        border: 1px solid #00ffff30;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0, 255, 255, 0.1);
        margin: 10px 0;
        padding: 15px;
        animation: messageSlide 0.5s ease-out;
    }
    
    @keyframes messageSlide {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* User message styling */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #ff008020 0%, #ff008040 100%);
        border: 1px solid #ff0080;
        margin-left: 20%;
    }
    
    /* Assistant message styling */
    .stChatMessage[data-testid="assistant-message"] {
        background: linear-gradient(135deg, #00ffff20 0%, #00ffff40 100%);
        border: 1px solid #00ffff;
        margin-right: 20%;
    }
    
    /* Command input styling */
    .stChatInputContainer {
        background: linear-gradient(135deg, #2a0a0a 0%, #4a0a2a 100%);
        border: 2px solid #ff0080;
        border-radius: 25px;
        box-shadow: 
            0 0 20px rgba(255, 0, 128, 0.3),
            inset 0 0 20px rgba(255, 0, 128, 0.1);
        animation: pulseGlow 2s ease-in-out infinite alternate;
        padding: 10px;
    }
    
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 20px rgba(255, 0, 128, 0.3), inset 0 0 20px rgba(255, 0, 128, 0.1); }
        100% { box-shadow: 0 0 30px rgba(255, 0, 128, 0.6), inset 0 0 30px rgba(255, 0, 128, 0.2); }
    }
    
    .stChatInputContainer input {
        background: transparent !important;
        color: #ff0080 !important;
        font-family: 'Rajdhani', sans-serif !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        border: none !important;
        text-shadow: 0 0 5px #ff008080 !important;
    }
    
    .stChatInputContainer input::placeholder {
        color: #ff008080 !important;
        text-shadow: 0 0 5px #ff008040 !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #00ffff20 0%, #00ffff40 100%);
        border: 1px solid #00ffff;
        border-radius: 10px;
        color: #00ffff;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00ffff40 0%, #00ffff60 100%);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.4);
        transform: translateY(-2px);
    }
    
    /* Toggle styling */
    .stCheckbox, .stToggle {
        color: #00ffff;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
    }
    
    /* Form styling */
    .stForm {
        background: linear-gradient(135deg, #1a1a3a 0%, #2a2a4a 100%);
        border: 1px solid #00ffff30;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0, 255, 255, 0.1);
    }
    
    /* Text input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: linear-gradient(135deg, #0a0a1f 0%, #1a1a2f 100%) !important;
        border: 1px solid #00ffff30 !important;
        border-radius: 10px !important;
        color: #e0e0ff !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    /* Sidebar headers */
    .sidebar-header {
        color: #00ffff;
        font-family: 'Orbitron', monospace;
        font-weight: 700;
        text-shadow: 0 0 10px #00ffff40;
        border-bottom: 2px solid #00ffff40;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    
    /* Status indicators */
    .status-active {
        color: #00ff80;
        text-shadow: 0 0 10px #00ff8040;
    }
    
    .status-inactive {
        color: #ff8080;
        text-shadow: 0 0 10px #ff808040;
    }
    
    /* File uploader styling */
    .stFileUploader {
        background: linear-gradient(135deg, #1a1a3a 0%, #2a2a4a 100%);
        border: 2px dashed #00ffff40;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
    }
    
    .stFileUploader:hover {
        border-color: #00ffff80;
        background: linear-gradient(135deg, #2a2a4a 0%, #3a3a5a 100%);
    }
    
    /* Alert styling */
    .stAlert {
        background: linear-gradient(135deg, #ff008020 0%, #ff008040 100%);
        border: 1px solid #ff0080;
        border-radius: 10px;
        color: #ff80c0;
    }
    
    /* Success message styling */
    .stSuccess {
        background: linear-gradient(135deg, #00ff8020 0%, #00ff8040 100%);
        border: 1px solid #00ff80;
        border-radius: 10px;
        color: #80ffc0;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, #1a1a3a 0%, #2a2a4a 100%);
        border: 1px solid #00ffff30;
        border-radius: 10px;
        color: #00ffff;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a3a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00ffff 0%, #ff0080 100%);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #00ffff80 0%, #ff008080 100%);
    }
    
    /* Attachment preview styling */
    .attachment-preview {
        background: linear-gradient(135deg, #2a2a4a 0%, #3a3a5a 100%);
        border: 1px solid #00ffff30;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .attachment-icon {
        color: #00ffff;
        font-size: 1.5rem;
    }
    
    .attachment-info {
        flex-grow: 1;
        color: #e0e0ff;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* Loading spinner override */
    .stSpinner {
        border-color: #00ffff !important;
    }
    
    /* Caption styling */
    .stCaption {
        color: #a0a0c0 !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    </style>
    """, unsafe_allow_html=True)

def setup_ui():
    """Configure the Streamlit UI layout and styling"""
    st.set_page_config(page_title="MagicMinute", page_icon="✉️", layout="wide")
    load_futuristic_css()

    # Animated neon logo
    st.markdown("""
    <div class="neon-logo">
        MAGIC MINUTE
    </div>
    <div class="subtitle">
        🤖 Advanced AI Email Assistant • Retro-Future Interface
    </div>
    """, unsafe_allow_html=True)

def render_auto_reply_sidebar(agent):
    """Render the auto-reply settings sidebar"""
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">🤖 AI AUTO-REPLY SYSTEM</h2>', unsafe_allow_html=True)
        
        # System Status
        status_text = "ACTIVE" if agent.config["active"] else "INACTIVE"
        status_class = "status-active" if agent.config["active"] else "status-inactive"
        st.markdown(f'<p class="{status_class}">● STATUS: {status_text}</p>', unsafe_allow_html=True)
        
        # Enable/Disable Toggle
        auto_reply_active = st.toggle(
            "🔥 ENABLE AUTO-REPLY",
            value=agent.config["active"],
            key="auto_reply_toggle",
            on_change=lambda: agent.toggle_active(
                st.session_state.auto_reply_toggle
            )
        )
        
        # Smart Replies Toggle (global setting)
        smart_replies_active = st.toggle(
            "🧠 SMART AI REPLIES",
            value=agent.smart_replies_enabled,
            key="smart_replies_toggle",
            on_change=lambda: agent.toggle_smart_replies(
                st.session_state.smart_replies_toggle
            ),
            help="AI-powered contextual responses"
        )
        
        # Rule Management
        with st.expander("⚙️ MANAGE RULES"):
            # Add New Rule Form
            with st.form("add_rule_form"):
                st.write("**➕ ADD NEW RULE**")
                senders = st.text_input("📧 For emails from:", 
                                       placeholder="Leave empty for all emails")
                message = st.text_area("💬 Reply message:", 
                                     value="I'm currently unavailable. I'll respond soon.")
                col1, col2 = st.columns(2)
                start_time = col1.time_input("⏰ From:", value=datetime.strptime("09:00", "%H:%M").time())
                end_time = col2.time_input("⏰ Until:", value=datetime.strptime("17:00", "%H:%M").time())
                
                if st.form_submit_button("🚀 ADD RULE"):
                    new_rule = {
                        "senders": [s.strip() for s in senders.split(",")] if senders else [],
                        "message": message,
                        "start_time": start_time.strftime("%H:%M"),
                        "end_time": end_time.strftime("%H:%M"),
                        "use_llm": True,
                        "default": not bool(senders)
                    }
                    agent.add_rule(new_rule)
                    st.success("✅ Rule added successfully!")
            
            # Current Rules List
            st.write("**📋 ACTIVE RULES**")
            if not agent.config["rules"]:
                st.markdown('<p class="status-inactive">No rules configured</p>', unsafe_allow_html=True)
            else:
                for i, rule in enumerate(agent.config["rules"]):
                    cols = st.columns([0.8, 0.2])
                    with cols[0]:
                        st.markdown(f"""
                        <div class="attachment-preview">
                            <div class="attachment-icon">⏰</div>
                            <div class="attachment-info">
                                <strong>{rule['start_time']} - {rule['end_time']}</strong><br>
                                📩 {', '.join(rule['senders']) if rule['senders'] else 'All emails'}<br>
                                💬 {rule['message'][:30]}...
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    with cols[1]:
                        if st.button("🗑️", key=f"del_rule_{i}"):
                            agent.remove_rule(i)
                            st.rerun()

        # File Upload Section
        st.markdown('<h3 class="sidebar-header">📎 ATTACH FILES</h3>', unsafe_allow_html=True)
        uploaded_files = st.file_uploader(
            "🚀 Upload attachments",
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'txt', 'csv', 'xlsx'],
            help="Drag & drop files or click to browse"
        )
        
        return uploaded_files

def render_chat_interface(agent, uploaded_files):
    """Render the main chat interface"""
    # Handle file uploads
    if uploaded_files:
        st.session_state.attachments = []
        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.read()
            st.session_state.attachments.append({
                "name": uploaded_file.name,
                "bytes": file_bytes,
                "type": uploaded_file.type
            })
        
        # Display uploaded files
        with st.sidebar:
            st.markdown("**📁 ATTACHED FILES:**")
            for file in st.session_state.attachments:
                file_icon = "🖼️" if file["type"].startswith("image/") else "📄"
                st.markdown(f"""
                <div class="attachment-preview">
                    <div class="attachment-icon">{file_icon}</div>
                    <div class="attachment-info">
                        <strong>{file['name']}</strong><br>
                        <small>{file['type']}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Display chat history
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            if msg.get("preview"):
                st.markdown(f"**📧 To:** {msg['recipient']}")
                st.markdown(f"**📋 Subject:** {msg['subject']}")
                if st.session_state.attachments:
                    st.markdown("**📎 Attachments:**")
                    for file in st.session_state.attachments:
                        file_icon = "🖼️" if file["type"].startswith("image/") else "📄"
                        st.markdown(f"  {file_icon} {file['name']}")
                unique_key = f"draft_{i}_{hash(msg['body'])}"
                st.text_area("📝 Email Body", 
                            value=msg["body"], 
                            height=200, 
                            disabled=True, 
                            key=unique_key)
            else:
                st.write(msg["content"])

    # Chat input
    if prompt := st.chat_input("🤖 Enter your AI command..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            with st.spinner("🔄 Processing AI command..."):
                try:
                    lower_prompt = prompt.lower()
                    
                    # Immediate send commands
                    if any(cmd in lower_prompt for cmd in ["send now", "send it", "send immediately", "send this"]):
                        if st.session_state.current_draft:
                            if send_email(
                                st.session_state.current_draft["recipient"],
                                st.session_state.current_draft["subject"],
                                st.session_state.current_draft["body"],
                                st.session_state.attachments
                            ):
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": f"🚀 **EMAIL SENT SUCCESSFULLY**\n\n📧 **To:** {st.session_state.current_draft['recipient']}\n✨ **Status:** Delivered to inbox"
                                })
                                st.session_state.attachments = []
                                st.session_state.current_draft = None
                                st.rerun()
                        else:
                            st.error("❌ No draft available. Please compose an email first.")
                        
                    
                    # Auto-reply commands
                    elif lower_prompt.startswith(("auto-reply", "autoreply", "set auto-reply", "configure auto-reply")):
                        response = agent.handle_natural_language_command(prompt)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"🤖 **AUTO-REPLY SYSTEM UPDATE**\n\n{response}"
                        })
                        st.rerun()
                    
                    # Handle scheduling commands
                    elif "schedule" in lower_prompt and st.session_state.current_draft:
                        time_match = re.search(r'at (\d{1,2}(:\d{2})?[ap]m?|\d{1,2}:\d{2})', lower_prompt)
                        if time_match:
                            time_str = parse_time(time_match.group(1))
                            if time_str:
                                try:
                                    schedule_email_background(
                                        recipient=st.session_state.current_draft["recipient"],
                                        subject=st.session_state.current_draft["subject"],
                                        body=st.session_state.current_draft["body"],
                                        time_str=time_str
                                    )
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": f"⏰ **EMAIL SCHEDULED**\n\n📧 **To:** {st.session_state.current_draft['recipient']}\n🕐 **Time:** {time_str}\n✨ **Status:** Queued for delivery"
                                    })
                                    st.session_state.current_draft = None
                                    st.session_state.attachments = []
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Scheduling failed: {str(e)}")
                            else:
                                st.error("❌ Invalid time format. Use formats like '11:30pm' or '23:30'")
                        else:
                            st.error("❌ Please specify a time (e.g., 'schedule at 11:30pm')")
                    
                    # Normal LLM processing for other commands
                    else:
                        parsed = interpret_task_with_llm(prompt, st.session_state.current_draft)
                        
                        if parsed.get("task_type") == "unknown":
                            st.markdown("""
                            ❓ **Command not recognized. Try these:**
                            
                            🔹 **'Send this draft'** - Send current email
                            🔹 **'Schedule at 11:30pm'** - Schedule email delivery  
                            🔹 **'Email John about project update'** - Compose new email
                            🔹 **'Auto-reply: Set vacation message from 9am to 5pm'** - Configure auto-replies
                            """)
                        else:
                            recipient = resolve_email(parsed.get("recipient"))
                            subject = parsed.get("subject", "From MagicMinute")
                            body = parsed.get("body", "")
                            
                            # Handle scheduling from LLM
                            if parsed.get("schedule"):
                                time_str = parse_time(parsed["schedule"])
                                if time_str:
                                    try:
                                        schedule_email_background(
                                            recipient=recipient,
                                            subject=subject,
                                            body=body,
                                            time_str=time_str
                                        )
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": f"⏰ **EMAIL SCHEDULED**\n\n📧 **To:** {recipient}\n🕐 **Time:** {time_str}\n✨ **Status:** Queued for delivery"
                                        })
                                        st.session_state.current_draft = None
                                        st.session_state.attachments = []
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Scheduling failed: {str(e)}")
                                else:
                                    st.error("❌ Invalid time format received")
                            
                            # Handle draft vs send logic
                            elif parsed.get("show_draft") or any(cmd in lower_prompt for cmd in ["draft", "show", "preview"]):
                                st.session_state.current_draft = {
                                    "recipient": recipient,
                                    "subject": subject,
                                    "body": body
                                }
                                response_msg = {
                                    "role": "assistant",
                                    "preview": True,
                                    **st.session_state.current_draft,
                                    "content": "📝 **DRAFT READY FOR REVIEW**"
                                }
                                
                                if parsed.get("follow_up"):
                                    response_msg["follow_up"] = parsed["follow_up"]
                                
                                st.session_state.messages.append(response_msg)
                            else:
                                if send_email(recipient, subject, body, st.session_state.attachments):
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": f"🚀 **EMAIL SENT SUCCESSFULLY**\n\n📧 **To:** {recipient}\n✨ **Status:** Delivered to inbox"
                                    })
                                    st.session_state.attachments = []
                                    st.session_state.current_draft = None
                            
                            st.rerun()
                
                except Exception as e:
                    st.error(f"❌ System Error: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "🔧 **SYSTEM ERROR** - Please try again or rephrase your command."
                    })

    # Footer with system info
    st.markdown("""
    ---
    <div style="text-align: center; color: #666; font-family: 'Rajdhani', sans-serif;">
        🤖 MagicMinute AI Assistant v2.0 | Powered by Advanced Neural Networks<br>
        ⚡ Real-time Processing | 🔒 Secure Gmail Integration | 🌐 Cloud-Based Architecture
    </div>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_draft" not in st.session_state:
        st.session_state.current_draft = None
    if "attachments" not in st.session_state:
        st.session_state.attachments = []
    if 'auto_reply_agent' not in st.session_state:
        st.session_state.auto_reply_agent = AutoReplyAgent()
        st.session_state.auto_reply_agent.start_auto_reply()

def main():
    """Main UI entry point"""
    setup_ui()
    initialize_session_state()
    uploaded_files = render_auto_reply_sidebar(st.session_state.auto_reply_agent)
    render_chat_interface(st.session_state.auto_reply_agent, uploaded_files)

if __name__ == "__main__":
    main()
