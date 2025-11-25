from services.data_manager import load_payload, save_data
import streamlit as st 
import json
from services.llm_services import process_email, process_global_query, generate_draft, categorize_email, extract_action_items, generate_auto_reply
from services.utils import convert_to_relative_format, validate_email
import time

# --- Helper Functions ---

def format_email(email: dict) -> str:
    """
    Formats email details into a readable string for the LLM.
    Includes metadata like sender, timestamp, and the full body.
    """
    return f"Sender's_name : {email['name']}\nSender's email : {email['sender']}\nRecieved at : {email['timestamp']}\nSubject : {email['subject']}\nBody : {email['body']}"

def select_email(email: dict) -> None:
    """Updates the session state with the currently selected email."""
    st.session_state['selected_email'] = email

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Email Assistant")

# --- Session State Initialization ---
# Initialize session state variables if they don't exist.
# This ensures data persists across Streamlit reruns.

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
    
    # "Process Emails" button logic (only visible in Inbox view)
    if nav_selection == "Inbox":
        if st.button("Process Emails", type="primary"):
            with st.status("Processing Emails...", expanded=True) as status:
                st.write("Categorizing and extracting actions...")
                progress_bar = st.progress(0)
                
                # Iterate through emails and apply LLM services
                for ind, email in enumerate(st.session_state["emails"]):
                    # Use robust functions for categorization and action extraction
                    tags = categorize_email(format_email(email), st.session_state["prompts"]["categorization"])
                    action_items = extract_action_items(format_email(email), st.session_state['prompts']['action_extraction'])
                    
                    # Update session state with results
                    st.session_state['emails'][ind]['tags'] = tags
                    st.session_state['emails'][ind]['action_item'] = action_items
                    progress_bar.progress((ind + 1) / len(st.session_state["emails"]))
                
                status.update(label="Processing Completed!", state="complete", expanded=False)
            
            # Persist changes to disk
            save_data("mock_inbox.json", st.session_state["emails"])
            time.sleep(1)
            st.rerun()

# --- Main Content Area ---

# 1. Prompt Configuration View
if nav_selection == "Prompt Configuration":
    st.header("⚙️ Prompt Configuration")
    st.markdown("Customize the instructions for the AI agent below.")
   
    with st.form(key="prompt_form"):
        category = st.text_area(label="**Categorization Instructions**", value=st.session_state["prompts"]["categorization"], height=200, placeholder="Enter Categorization Prompt eg: Categorize the email into one of the following categories: Meeting, Task, Information, Other.")
        action = st.text_area(label="**Action Extraction Instructions**", value=st.session_state["prompts"]["action_extraction"], height=200, placeholder="Enter Action Prompt eg: Extract action items from the email with task and deadline.")
        reply = st.text_area(label="**Auto-reply Instructions**", value=st.session_state["prompts"]["auto_reply"], height=200, placeholder="Enter Auto-reply Prompt eg: Generate an auto-reply for the email with a professional tone.")
        
        button_container = st.container()
        with button_container:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
            with col3:
                submit = st.form_submit_button("Save Prompts", use_container_width=True)
    
    if submit:
        st.session_state["prompts"]["auto_reply"] = reply
        st.session_state["prompts"]["categorization"] = category
        st.session_state['prompts']["action_extraction"] = action
        save_data("prompts.json", st.session_state["prompts"])
        st.success("Prompts saved successfully!")

# 2. Inbox View
if nav_selection == "Inbox":
    st.header("📨 Inbox")
    
    # Header with "Compose New" button
    col_header, col_compose = st.columns([0.88, 0.12])
    with col_compose:
        if st.button("➕ Compose New"): 
            st.session_state["compose_mode"] = not st.session_state["compose_mode"]

    # Compose Email Modal
    if st.session_state["compose_mode"]:
        with st.container(border=True):
            st.subheader("New Email Draft")
            
            # Form for draft generation inputs
            with st.form(key="compose_form"):
                recipient_name = st.text_input("Name (Optional):")
                recipient_email = st.text_input("To:")
                new_subject = st.text_input("Subject:")
                new_prompt = st.text_area("Instructions for AI (e.g., 'Ask for a meeting next Tuesday'):")
                
                c1, c2 = st.columns([0.2, 0.8])
                with c1:
                    generate_submitted = st.form_submit_button("Generate Draft")
            
            # Handle draft generation
            if generate_submitted:
                if recipient_email and new_subject and new_prompt:
                    if validate_email(recipient_email):
                        with st.spinner("Drafting..."):
                            draft_body = generate_draft(new_prompt, recipient_name, recipient_email, new_subject)
                            st.session_state["new_draft_body"] = draft_body
                    else:
                        st.warning("Please provide a valid email address!")
                else:
                    st.warning("Please fill in all fields.")
            
            # Show generated draft and allow saving
            if "new_draft_body" in st.session_state:
                with st.form(key="save_draft_form"):
                    final_body = st.text_area("Generated Body:", value=st.session_state["new_draft_body"], height=200)
                    save_submitted = st.form_submit_button("Save to Drafts")
                
                if save_submitted:
                    new_draft = {
                        "recipient": f"{str(recipient_name + ' | ') if recipient_name else ''}{recipient_email}",
                        "subject": new_subject,
                        "body": final_body,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    st.session_state["drafts"].append(new_draft)
                    save_data("new_compose.json", st.session_state["drafts"])
                    st.success("Draft saved.")
                    time.sleep(2)
                    st.session_state["compose_mode"] = False
                    del st.session_state["new_draft_body"]
                    st.rerun()
            
            if st.button("Cancel"):
                st.session_state["compose_mode"] = False
                if "new_draft_body" in st.session_state:
                    del st.session_state["new_draft_body"]
                st.rerun()

    # Split layout: Email List (Left) vs Details/Chat (Right)
    left_col, right_col = st.columns([0.45, 0.55])
    
    # --- Email List Column ---
    with left_col:
        # Filter controls
        show_unread = st.checkbox("Show Unread Only")
        
        with st.container(height=600):
            # Apply filters
            filtered_emails = [e for e in st.session_state["emails"] if not e.get("is_read")] if show_unread else st.session_state["emails"]
            
            if not filtered_emails:
                st.info("No unread emails found." if show_unread else "No emails found.")
                
            for email in filtered_emails:
                is_selected = (st.session_state["selected_email"] and st.session_state["selected_email"]['id'] == email['id'])
                
                # Auto-mark as read if selected
                if is_selected and not email.get('is_read'):
                    email['is_read'] = True
                    save_data("mock_inbox.json", st.session_state["emails"])

                # Visual styling for selected/unread emails
                card_border = True
                
                with st.container(border=card_border):
                    c1, c2 = st.columns([0.8, 0.2])
                    with c1:
                        # Bold sender name if unread
                        sender_style = "**" if not email.get('is_read') else ""
                        st.markdown(f"{sender_style}{email['name']}{sender_style}")
                        st.caption(email['subject'])
                        if email.get("tags"):
                            st.caption(f"🏷️ {', '.join(email['tags'])}")
                    with c2:
                        if st.button("Open", key=f"open_{email['id']}", type="primary" if is_selected else "secondary"):
                            select_email(email)
                            st.rerun()

    # --- Details / Chat Column ---
    with right_col:
        st.space(33) # Spacer to align with list
        if st.session_state["selected_email"]:
            email = st.session_state["selected_email"]
            
            # Initialize chat view state
            if "chat_view_active" not in st.session_state:
                st.session_state["chat_view_active"] = False
            
            # Reset view if a different email is selected
            if "last_selected_email_id" not in st.session_state:
                st.session_state["last_selected_email_id"] = email["id"]
            elif st.session_state["last_selected_email_id"] != email["id"]:
                st.session_state["chat_view_active"] = False
                st.session_state["last_selected_email_id"] = email["id"]

            with st.container(height=600, border=True):
                # Header: Subject + View Toggle
                header_col, btn_col = st.columns([0.75, 0.25])
                with header_col:
                    st.subheader(email["subject"])
                with btn_col:
                    if st.session_state["chat_view_active"]:
                        if st.button("⬅️ Back to Details", key="back_btn"):
                            st.session_state["chat_view_active"] = False
                            st.rerun()
                    else:
                        if st.button("💬 Chat with Email", key="chat_btn"):
                            st.session_state["chat_view_active"] = True
                            st.rerun()
                
                st.divider()

                # --- Chat View ---
                if st.session_state["chat_view_active"]:
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

                # --- Details View ---
                else:
                    st.caption(f"From: {email['name']} <{email['sender']}> |  {convert_to_relative_format(email['timestamp'])}")
                    st.markdown(email["body"])
                    
                    # Display Action Items
                    action_items = email.get("action_item")
                    if action_items and "error" not in action_items:
                        st.divider()
                        st.subheader("⚡ Action Items")
                        task = action_items.get("task", "Unknown Task")
                        deadline = action_items.get("deadline", "No Deadline")
                        st.info(f"**Task:** {task}\n\n**Due:** {deadline}")

                    # Reply Generation Section
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        if st.button("Generate Reply", use_container_width=True):
                            with st.spinner("Generating..."):
                                reply_draft = generate_auto_reply(format_email(email), st.session_state["prompts"]["auto_reply"])
                                email['reply'] = reply_draft
                                save_data("mock_inbox.json", st.session_state["emails"])
                            st.rerun()
                    
                    # Draft Editor
                    if email.get("reply"):
                        with st.expander(label="Draft Reply", expanded=False):
                            with st.form(key=f"edit_reply_form_{email['id']}"):
                                edited_reply = st.text_area(label="", value=email["reply"], height=150)
                                save_draft_btn = st.form_submit_button("Save Draft")
                                
                            if save_draft_btn:
                                email["reply"] = edited_reply
                                save_data("mock_inbox.json", st.session_state["emails"])
                                st.success("Draft saved.")
        else:
            st.info("Select an email to view details.")

# 3. Composed Mails View
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

# 4. Global Agent View
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
                    # Pass the last 3 messages as context to the LLM
                    chat_history = st.session_state["global_chat"][-3:] if len(st.session_state["global_chat"]) > 0 else []
                    response = process_global_query(st.session_state["emails"], prompt, chat_history)
                    st.markdown(response)
        st.session_state["global_chat"].append({"role": "assistant", "message": response})
        st.rerun()
