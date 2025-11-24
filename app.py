from services.data_manager import load_payload,save_data
import streamlit as st 
import json
from services.llm_services import process_email
from services.utils import parse_json_output,parse_list_output
import time

def format_email(email:dict)->str:
    """Extracts relevant details from email and returns string"""
    return f"Sender's_name : {email["name"] }/n Sender's email : {email["sender"]} /n Recieved at : {email["timestamp"]} /n Subject : {email["body"]} /n Body : {email["body"]}"

def select_email(email:dict)->None:
    st.session_state['selected_email'] = email
st.set_page_config(layout="wide")
st.title("📧Email Assistant")
with st.container(height=500):
    if "emails" not in st.session_state:
        emails = load_payload("mock_inbox.json")
        st.session_state["emails"] = emails

    if "prompts" not in st.session_state:
        prompts = load_payload("prompts.json")
        st.session_state["prompts"] = prompts

    if "selected_email" not in st.session_state:
        st.session_state["selected_email"] = None# will contain dictionary of mails
    left_col,right_col = st.columns([0.5,0.5])

    if "email_chats" not in st.session_state:
        st.session_state["email_chats"] = {}
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


    st.sidebar.header("⚙️Prompt configration")

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
    process_email_button = st.sidebar.button("Process Emails")

    if process_email_button:

        with st.spinner("Processing..."):
            progress_bar = st.progress(0)
            for ind,email in enumerate(st.session_state["emails"]):
                
                    # st.write(f"Processing email {email['id']}")
                category_response = process_email(email['body'] , st.session_state["prompts"]["categorization"])
                action_response = process_email(email['body'] , st.session_state['prompts']['action_extraction'])
                    
                st.session_state['emails'][ind]['tags'] = parse_list_output(category_response)
                st.session_state['emails'][ind]['action_item'] = parse_json_output(action_response)
                progress_bar.progress((ind+1)/len(st.session_state["emails"]))
            save_data("mock_inbox.json" , st.session_state["emails"])
            st.success("Process Completed")
            time.sleep(1)
            st.rerun()


    # with left_col:
    #     st.header("Inbox")
    #     for email in st.session_state["emails"]:
    #         selected = (st.session_state["selected_email"] and st.session_state["selected_email"]["id"] == email["id"])
    #         expander = st.expander(f"**{email["name"]}** - {email['subject']}")
    #         expander.caption(f"Timestamp : {email["timestamp"]}")
    #         expander.write(f"**Tag** : {email['tags']}")
    #         expander.write("---")
    #         expander.write(email['body'])
    #         expander.button("Chat with this email" ,type = "primary" if selected else "secondary", on_click = select_email , args = (email,) , key = f"{email['id']}")


    #     process_email_button = st.button("Process Emails")

    #     if process_email_button:

    #         with st.spinner("Processing..."):
    #             progress_bar = st.progress(0)
    #             for ind,email in enumerate(st.session_state["emails"]):
                    
    #                 # st.write(f"Processing email {email['id']}")
    #                 category_response = process_email(email['body'] , st.session_state["prompts"]["categorization"])
    #                 action_response = process_email(email['body'] , st.session_state['prompts']['action_extraction'])
                    
    #                 st.session_state['emails'][ind]['tags'] = parse_list_output(category_response)
    #                 st.session_state['emails'][ind]['action_item'] = parse_json_output(action_response)
    #                 progress_bar.progress((ind+1)/len(st.session_state["emails"]))
    #             save_data("mock_inbox.json" , st.session_state["emails"])
    #             st.success("Process Completed")
    #             time.sleep(1)
    #             st.rerun()

    # with col2:
    #     refresh = st.button("Refresh Selection")

    #     for expands in expanders:
    #         if expands['expander'].expanded:
    #             st.session_state["selected"].append(expands['email_id'])
    #             st.write(f"This email is open {expands['email_id']}")
    #         elif expands['id'] in st.session_state["selected"]:
    #             st.session_state["selected"].remove(expands['id'])

    # with right_col:
    #     if st.session_state["selected_email"]:
    #         if st.session_state["selected_email"]["id"] not in st.session_state["email_chats"]:
    #             st.session_state["email_chats"][st.session_state["selected_email"]["id"]] = []
            
    #         for chat in st.session_state["email_chats"][st.session_state["selected_email"]["id"]]:
    #             with st.chat_message(chat["role"]):
    #                 st.markdown(chat["message"])
            
    #         if prompt:=st.chat_input("Say something"):
    #             with st.chat_message("user"):
    #                 st.markdown(prompt)
    #             st.session_state["email_chats"][st.session_state["selected_email"]["id"]].append({"role":"user","message":prompt})

    #             with st.chat_message("assistant"):
    #                 email = st.session_state["selected_email"]
    #                 llm_response = process_email(format_email(email),prompt)
    #                 st.markdown(llm_response)
    #             st.session_state["email_chats"][st.session_state["selected_email"]["id"]].append({"role":"assistant","message":llm_response})
    #     else:
    #         st.info("Select an email to start chatting.")
            

    # --- Helper Function for LLM Context ---
    def format_email_context(email):
        return f"""
        From: {email['sender']} ({email['name']})
        Date: {email['timestamp']}
        Subject: {email['subject']}
        
        Body:
        {email['body']}
        """



        

    with left_col:
        st.header("Inbox")
        with st.container(height=500):
            for email in st.session_state["emails"]:
                selected = (st.session_state["selected_email"] and st.session_state["selected_email"]['id'] == email['id'])
                if selected:
                    email['is_read'] = True
                    save_data("mock_inbox.json",st.session_state["emails"])
                with st.container(border=True,width="stretch"):
                    col1,col2 = st.columns([0.7,0.3])
                    with col1:
                        if not email['is_read']:
                            st.write(f"**{email["name"]}** : {email["subject"]}")
                            if email["tags"]:
                                st.text(f"🏷️ {", ".join(email["tags"])}")
                        else:
                            st.caption(f"**{email["name"]}** : {email["subject"]}")
                            if email["tags"]:
                                st.caption(f"🏷️ {", ".join(email["tags"])}")
                        
                    with col2:
                        flex = st.container(horizontal_alignment="right")
                        flex.button("Open" , on_click = select_email , args=(email,) , type = "primary" if selected else "secondary" , key=f"{email["id"]}" , width="content")

    with right_col:
        st.space(59)
        with st.container(height=500):
            if st.session_state["selected_email"]:
                
                with st.container(border = True):
                    email = st.session_state["selected_email"]
                    st.header(f"{email["subject"]}")
                    st.caption(f"From: {email["name"]}\<{email["sender"]}\>")
                    st.caption(st.session_state["selected_email"]["timestamp"])
                    st.divider()
                    with st.container(height=200,border=None):
                        st.markdown(st.session_state['selected_email']["body"])
                    if st.button("Generate reply"):
                        with st.expander("Generated Reply(*Draft*)"):
                            st.text_area("This is demo reply",value="This is content")
                            
                            col1,col2 = st.columns([0.5,0.5])
                            with col1:
                                st.button("Save")
                            with col2:
                                flex=st.container(horizontal_alignment="right")
                                flex.button("Send")

                    st.divider()
                    st.header("Email Agent")
                    if st.session_state["selected_email"]["id"] not in st.session_state["email_chats"]:
                        st.session_state["email_chats"][st.session_state["selected_email"]["id"]] = []
                    messages = st.container()
                    for chat in st.session_state["email_chats"][st.session_state["selected_email"]["id"]]:
                        with messages.chat_message(chat["role"]):
                            st.markdown(chat["message"])
                        
                    if prompt:=messages.chat_input("Say something"):
                        with messages.chat_message("user"):
                                st.markdown(prompt)
                        st.session_state["email_chats"][st.session_state["selected_email"]["id"]].append({"role":"user","message":prompt})

                        with messages.chat_message("assistant"):
                            email = st.session_state["selected_email"]
                            llm_response = process_email(format_email(email),prompt)
                            st.markdown(llm_response)
                        st.session_state["email_chats"][st.session_state["selected_email"]["id"]].append({"role":"assistant","message":llm_response})
            else:
                st.info("Select an email to start chatting.")