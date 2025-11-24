from services.data_manager import load_payload, save_data
import streamlit as st 
import json
from services.llm_services import process_email, process_global_query, generate_draft
from services.utils import parse_json_output, parse_list_output
import time

# --- Helper Functions ---
def format_email(email: dict) -> str:
    """Extracts relevant details from email and returns string"""
    return f"Sender's_name : {email['name']}\nSender's email : {email['sender']}\nRecieved at : {email['timestamp']}\nSubject : {email['subject']}\nBody : {email['body']}"

def format_email_for_reply(email: dict) -> str:
    """Extracts relevant details from email and returns string"""
    return f"Sender's_name : {email['name']}\nSender's email : {email['sender']}\nRecieved at : {email['timestamp']}\nSubject : {email['subject']}\nBody : {email['body']}\nTags : {email.get('tags', [])}\nAction Item : {email.get('action_item', {})}"

def select_email(email: dict) -> None:
    st.session_state['selected_email'] = email

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Email Assistant")

# --- Session State Initialization ---
if "emails" not in st.session_state:
    st.session_state["emails"] = load_payload("mock_inbox.json")

if "prompts" not in st.session_state:
    st.session_state["prompts"] = load_payload("prompts.json")

if "selected_email" not in st.session_state:
    st.session_state["selected_email"] = None

if "email_chats" not in st.session_state:
    st.session_state["email_chats"] = {}

if "global_chat" not in st.session_state:
    st.session_state["global_chat"] = []

if "compose_mode" not in st.session_state:
    st.session_state["compose_mode"] = False

if "drafts" not in st.session_state:
    st.session_state["drafts"] = load_payload("new_compose.json")

# --- Sidebar Navigation ---
with st.sidebar:
    st.title("📧 Email Assistant")
    nav_selection = st.radio("**Navigation**", ["Inbox", "Global Agent", "Composed Mails", "Prompt Configuration"])
    
    st.divider()
    if nav_selection == "Inbox":
        if st.button("Process Emails", type="primary"):
            with st.status("Processing Emails...", expanded=True) as status:
                st.write("Categorizing and extracting actions...")
                progress_bar = st.progress(0)
                for ind, email in enumerate(st.session_state["emails"]):
                    category_response = process_email(format_email(email), st.session_state["prompts"]["categorization"])
                    action_response = process_email(format_email(email), st.session_state['prompts']['action_extraction'])
                    
                    st.session_state['emails'][ind]['tags'] = parse_list_output(category_response)
                    st.session_state['emails'][ind]['action_item'] = parse_json_output(action_response)
                    progress_bar.progress((ind + 1) / len(st.session_state["emails"]))
                status.update(label="Processing Completed!", state="complete", expanded=False)
            save_data("mock_inbox.json", st.session_state["emails"])
            time.sleep(1)
            st.rerun()

# --- Main Content ---

if nav_selection == "Prompt Configuration":
    st.header("⚙️ Prompt Configuration")
   
    with st.form(key="prompt_form"):
        category = st.text_area(label="**Categorization**", value=st.session_state["prompts"]["categorization"], height=350)
        action = st.text_area(label="**Action**", value=st.session_state["prompts"]["action_extraction"], height=350)
        reply = st.text_area(label="**Auto-reply**", value=st.session_state["prompts"]["auto_reply"], height=350)
        button_container = st.container(horizontal=True)
        with button_container:
            col1,col2,col3,col4,col5 = st.columns([1,1,2,1,1])
            with col3:
                submit = st.form_submit_button("Save  Prompts",width="stretch")
    if submit:
        st.session_state["prompts"]["auto_reply"] = reply
        st.session_state["prompts"]["categorization"] = category
        st.session_state['prompts']["action_extraction"] = action
        save_data("prompts.json", st.session_state["prompts"])
        st.success("Saved Prompts")



if nav_selection == "Inbox":
    st.header("📨 Inbox")
    
    # Compose Button (Top Right of Inbox Container)
    col_header, col_compose = st.columns([0.85, 0.15])
    with col_compose:
        if st.button("➕ Compose New"): 
            st.session_state["compose_mode"] = not st.session_state["compose_mode"]

    # Compose Modal/Area
    if st.session_state["compose_mode"]:
        with st.container(border=True):
            st.subheader("New Email Draft")
            
            # Use a form to prevent reruns on every keystroke
            with st.form(key="compose_form"):
                new_recipient = st.text_input("To:")
                new_subject = st.text_input("Subject:")
                new_prompt = st.text_area("Instructions for AI (e.g., 'Ask for a meeting next Tuesday'):")
                
                c1, c2 = st.columns([0.2, 0.8])
                with c1:
                    generate_submitted = st.form_submit_button("Generate Draft")
            
            if generate_submitted:
                if new_recipient and new_subject and new_prompt:
                    with st.spinner("Drafting..."):
                        draft_body = generate_draft(new_prompt, new_recipient, new_subject)
                        st.session_state["new_draft_body"] = draft_body
                else:
                    st.warning("Please fill in all fields.")
            
            if "new_draft_body" in st.session_state:
                with st.form(key="save_draft_form"):
                    st.text_area("Generated Body:", value=st.session_state["new_draft_body"], height=200)
                    save_submitted = st.form_submit_button("Save to Drafts")
                
                if save_submitted:
                    new_draft = {
                        "recipient": new_recipient, # Note: This might be lost if not persisted, but for now it's okay as it's in the same rerun cycle if generated
                        "subject": new_subject,
                        "body": st.session_state["new_draft_body"],
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state["drafts"].append(new_draft)
                    save_data("new_compose.json", st.session_state["drafts"])
                    st.success("Draft saved.")
                    st.session_state["compose_mode"] = False
                    del st.session_state["new_draft_body"]
                    st.rerun()
            
            if st.button("Cancel"):
                st.session_state["compose_mode"] = False
                if "new_draft_body" in st.session_state:
                    del st.session_state["new_draft_body"]
                st.rerun()

    # Inbox Layout
    left_col, right_col = st.columns([0.4, 0.6])
    
    with left_col:
        with st.container(height=600):
            for email in st.session_state["emails"]:
                is_selected = (st.session_state["selected_email"] and st.session_state["selected_email"]['id'] == email['id'])
                
                # Mark as read if selected
                if is_selected and not email.get('is_read'):
                    email['is_read'] = True
                    save_data("mock_inbox.json", st.session_state["emails"])

                # Email Card Style
                card_border = True
                if is_selected:
                    card_border = True # Can add specific style if needed
                
                with st.container(border=card_border):
                    c1, c2 = st.columns([0.8, 0.2])
                    with c1:
                        sender_style = "**" if not email.get('is_read') else ""
                        st.markdown(f"{sender_style}{email['name']}{sender_style}")
                        st.caption(email['subject'])
                        if email.get("tags"):
                            st.caption(f"🏷️ {', '.join(email['tags'])}")
                    with c2:
                        if st.button("Open", key=f"open_{email['id']}", type="primary" if is_selected else "secondary"):
                            select_email(email)
                            st.rerun()

    with right_col:
        if st.session_state["selected_email"]:
            email = st.session_state["selected_email"]
            with st.container(height=600, border=True):
                st.subheader(email["subject"])
                st.caption(f"From: {email['name']} <{email['sender']}> | {email['timestamp']}")
                st.divider()
                st.markdown(email["body"])
                
                # Action Items
                action_items = email.get("action_item")
                if action_items and "error" not in action_items:
                    st.divider()
                    st.subheader("⚡ Action Items")
                    task = action_items.get("task", "Unknown Task")
                    deadline = action_items.get("deadline", "No Deadline")
                    st.info(f"**Task:** {task}\n\n**Due:** {deadline}")

                st.divider()
                
                # Reply Section
                st.subheader("Reply Agent")
                if st.button("Generate Reply"):
                    with st.spinner("Generating..."):
                        reply_draft = process_email(format_email_for_reply(email), st.session_state["prompts"]["auto_reply"])
                        email['reply'] = reply_draft
                        save_data("mock_inbox.json", st.session_state["emails"])
                        st.rerun()
                
                if email.get("reply"):
                    with st.expander(label="Draft Reply", expanded=True):
                        with st.form(key=f"edit_reply_form_{email['id']}"):
                            edited_reply = st.text_area(label="", value=email["reply"], height=150)
                            save_draft_btn = st.form_submit_button("Save Draft")
                            
                        if save_draft_btn:
                            email["reply"] = edited_reply
                            save_data("mock_inbox.json", st.session_state["emails"])
                            st.success("Draft saved.")

                st.divider()
                
                # Chat with Email
                st.subheader("Chat with this Email")
                chat_key = email["id"]
                if chat_key not in st.session_state["email_chats"]:
                    st.session_state["email_chats"][chat_key] = []
                
                chat_container = st.container()
                with chat_container:
                    for msg in st.session_state["email_chats"][chat_key]:
                        with st.chat_message(msg["role"]):
                            st.markdown(msg["message"])
                
                if prompt := st.chat_input("Ask about this email..."):
                    st.session_state["email_chats"][chat_key].append({"role": "user", "message": prompt})
                    with chat_container:
                        with st.chat_message("user"):
                            st.markdown(prompt)
                        
                        with st.chat_message("assistant"):
                            with st.spinner("Thinking..."):
                                response = process_email(format_email(email), prompt)
                                st.markdown(response)
                    st.session_state["email_chats"][chat_key].append({"role": "assistant", "message": response})
                    st.rerun()
        else:
            st.info("Select an email to view details.")

elif nav_selection == "Composed Mails":
    st.header("📂 Composed Mails")
    if not st.session_state["drafts"]:
        st.info("No drafts found.")
    else:
        for i, draft in enumerate(st.session_state["drafts"]):
            with st.container(border=True):
                st.subheader(f"To: {draft.get('recipient', 'Unknown')}")
                st.caption(f"Subject: {draft.get('subject', 'No Subject')} | {draft.get('timestamp', '')}")
                st.markdown(draft.get('body', ''))
                # Placeholder for edit/send functionality if needed
                # st.button("Edit", key=f"edit_draft_{i}") 

elif nav_selection == "Global Agent":
    st.header("🌐 Global Inbox Agent")
    st.markdown("Ask questions about your entire inbox (e.g., 'What are my most urgent tasks?', 'Summarize unread emails').")
    
    global_chat_container = st.container()
    with global_chat_container:
        for msg in st.session_state["global_chat"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["message"])
            
    if prompt := st.chat_input("Ask Global Agent..."):
        st.session_state["global_chat"].append({"role": "user", "message": prompt})
        with global_chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing Inbox..."):
                    response = process_global_query(st.session_state["emails"], prompt)
                    st.markdown(response)
        st.session_state["global_chat"].append({"role": "assistant", "message": response})
        st.rerun()
