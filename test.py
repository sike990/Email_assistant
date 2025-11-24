def select_email(email:dict)->None:
    st.session_state["selected_email"] = email
with left_col:
    st.header("Inbox")
    for email in st.session_state["emails"]:
        selected = (st.session["selected_email"] and st.session["selected_email"]['id'] = email['id'])
        with st.container():
            col1,col2 = st.coloumns([2,1])
            with col1:
                st.write(f"{email["name"]} : {email["subject"]}")
                if st.session_state["tags"]:
                    st.write(f"Tags : *{", ".join(st.session_state["tags"])}*")
            with col2:
                st.button("Open" , on_click = select_email , args=(email,) , type = "primary" if selected else "secondary", width="stretch")


with right_col:
    if st.session_state["selected"]:
        st.caption(st.session_state["selected_email"]["timestamp"])
        st.divider()
        st.markdown(st.session_state['selected_email']["body"])
        st.divider()
        st.header("Email Agent")
        

