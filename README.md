# Email Assistant

A prompt-driven Email Productivity Agent built with Streamlit and LangChain (Groq). This intelligent agent helps you manage your inbox by categorizing emails, extracting action items, drafting replies, and answering global queries about your inbox.

## Features

- **Inbox Management**: View emails with auto-generated categories and tags.
- **Action Item Extraction**: Automatically identifies tasks and deadlines from emails.
- **Email Agent Chat**: Chat with individual emails to summarize, ask questions, or generate replies.
- **Global Inbox Agent**: Ask questions across your entire inbox (e.g., "What are my urgent tasks?").
- **Compose & Drafts**: Draft new emails from scratch using AI prompts and save them for later.
- **Prompt Configuration**: Customize the "brain" of the agent by editing prompts for categorization, action extraction, and auto-replies.

## Setup Instructions

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd Email_assistent
    ```

2.  **Install Dependencies**:
    Ensure you have Python installed. It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: If `requirements.txt` is missing, you'll need `streamlit`, `langchain-groq`, `python-dotenv`, etc.)*

3.  **Environment Configuration**:
    Create a `.env` file in the root directory and add your Groq API key:
    ```
    GROQ_API_KEY=your_groq_api_key_here
    ```

4.  **Data Setup**:
    - `data/mock_inbox.json`: Contains the sample emails.
    - `data/prompts.json`: Stores user-defined prompts.
    - `data/new_compose.json`: Stores drafted emails.

## How to Run

Run the Streamlit application:
```bash
streamlit run app.py
```

The application will open in your default web browser (usually at `http://localhost:8501`).

## Usage Guide

### Inbox
- **View Emails**: Scroll through the list of emails. Important/Unread emails are highlighted.
- **Open Email**: Click "Open" to view details, extracted action items, and the chat interface.
- **Compose New**: Click the "➕ Compose New" button to draft a new email. Enter a prompt (e.g., "Invite John to the party") and let the AI write the body. Save it to drafts.

### Global Agent
- Navigate to "Global Agent" in the sidebar.
- Ask high-level questions like:
    - "Summarize the newsletter emails."
    - "Do I have any deadlines today?"

### Draft Replies
- Navigate to "Draft Replies" in the sidebar to view your saved drafts.

### Configuration
- Navigate to "Configuration" to edit the system prompts for Categorization, Action Extraction, and Auto-reply.

## Project Structure

- `app.py`: Main Streamlit application.
- `services/`:
    - `data_manager.py`: Handles JSON file I/O.
    - `llm_services.py`: Interfaces with Groq LLM.
    - `utils.py`: Helper functions for parsing LLM output.
- `data/`: JSON storage for emails, prompts, and drafts.
