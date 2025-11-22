from services.data_manager import load_payload,save_data
import streamlit as st 
import json
from services.llm_services import process_email

st.title("Email Assistant")

if "emails" not in st.session_state:
    emails = load_payload("mock_inbox.json")
    st.session_state["emails"] = emails

if "prompts" not in st.session_state:
    prompts = load_payload("prompts.json")
    st.session_state["prompts"] = prompts



# action = st.sidebar.text_area(label="Action" , value = st.session_state["prompts"]["action_extraction"])
# action_button =  st.sidebar.button("Save Prompt")
# if action_button and action:
#     st.session_state['prompts']["action_extraction"] = action
#     file = st.session_state["prompts"]
#     save_data("prompts.json",file)
# elif action_button and not action:
#     st.write("Please provide some text to submit.")

# category = st.sidebar.text_area(label="Categorization" , value = st.session_state["prompts"]["categorization"])
# category_button =  st.sidebar.button("Save Prompt")
# if category_button and category:
#     st.session_state["prompts"]["categorization"] = category
#     file = st.session_state["prompts"]
#     save_data("prompts.json",file)
# elif category_button and not category:
#     st.write("Please provide some text to submit.")

# reply = st.sidebar.text_area(label="Auto-reply" , value = st.session_state["prompts"]["auto_reply"])
# reply_button =  st.sidebar.button("Save Prompt")
# if reply_button and reply:
#     st.session_state["prompts"]["auto_reply"] = reply
#     file = st.session_state["prompts"]
#     save_data("prompts.json",file)
# elif reply_button and not reply:
#     st.write("Please provide some text to submit.")

st.sidebar.header("AI configration")

with st.sidebar.form(key="prompt_form"):
    category = st.text_area(label="Categorization" , value = st.session_state["prompts"]["categorization"])
    action = st.text_area(label="Action" , value = st.session_state["prompts"]["action_extraction"])
    reply = st.text_area(label="Auto-reply" , value = st.session_state["prompts"]["auto_reply"])

    submit = st.form_submit_button("Save Prompt")

    if submit:
        st.session_state["prompts"]["auto_reply"] = reply
        st.session_state["prompts"]["categorization"] = category
        st.session_state['prompts']["action_extraction"] = action
        file = st.session_state["prompts"]
        save_data("prompts.json",file)


for email in st.session_state["emails"]:
    expander = st.expander(f"**{email["name"]}** - {email['subject']}")
    expander.caption(f"Timestamp : {email["timestamp"]}")
    expander.write(f"**Tag** : *{email['tags']}*")
    expander.write("----")
    expander.write(email['body'])


process_email = st.sidebar.button("Process Emails")

# if process_email:
#     for email in st.state_session['emails']:

