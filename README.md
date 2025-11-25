# Email Assistant

A smart, prompt-driven productivity tool designed to help you master your inbox. Built with Streamlit and powered by Groq's LLMs, this assistant automates the tedious parts of email management—categorization, action extraction, and drafting—so you can focus on what matters.

## Key Features

- **Intelligent Inbox**: Your emails are automatically tagged (e.g., "Important", "To-Do") and organized.
- **Action Extraction**: Never miss a deadline. The assistant scans your emails and highlights actionable tasks and due dates.
- **Smart Filtering**: Easily toggle the "Show Unread Only" filter to focus on what needs your immediate attention.
- **Context-Aware Chat**:
    - **Email Chat**: Ask questions about specific emails or request summaries.
    - **Global Agent**: Query your entire inbox (e.g., "What are my top priorities today?"). It now remembers your recent conversation context for a smoother experience.
- **AI-Powered Drafting**:
    - **Auto-Reply**: Generate professional replies with a single click.
    - **Compose from Scratch**: Provide a simple instruction (e.g., "Ask John for the Q3 report"), and let the AI draft a polished email for you.
- **Customizable "Brain"**: Tailor the agent's behavior by editing the system prompts for categorization, extraction, and tone directly from the configuration page.

## Setup Instructions

1.  **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd Email_assistent
    ```

2.  **Install Dependencies**:
    We recommend using a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```
    *(Ensure you have `streamlit`, `langchain-groq`, `python-dotenv`, and other requirements installed.)*

3.  **Environment Configuration**:
    Create a `.env` file in the root directory and add your Groq API key:
    ```
    GROQ_API_KEY=your_groq_api_key_here
    ```

4.  **Data Setup**:
    The application uses JSON files for local storage (simulating a database):
    - `data/mock_inbox.json`: Sample email data.
    - `data/prompts.json`: User-defined system prompts.
    - `data/new_compose.json`: Storage for your drafted emails.

## How to Run

Launch the application using Streamlit:
```bash
streamlit run app.py
```
The app will open automatically in your default browser at `http://localhost:8501`.

## Usage Guide

### 📨 Inbox
- **Browse & Filter**: Scroll through your emails or use the "Show Unread Only" checkbox to declutter your view.
- **Deep Dive**: Click "Open" on any email to view its full content, extracted action items, and to start a chat session specific to that email.
- **Compose**: Click the "➕ Compose New" button to draft a new email. Just give the AI a topic or instruction, and it will handle the writing.

### 🌐 Global Agent
- Switch to the "Global Agent" tab to ask high-level questions about your inbox.
- Example queries:
    - "Do I have any urgent emails from HR?"
    - "Summarize the newsletters I received today."
- The agent remembers the last few messages, so you can ask follow-up questions naturally.

### ⚙️ Configuration
- Visit the "Prompt Configuration" section to tweak how the AI behaves. You can adjust the instructions for how it categorizes emails, extracts tasks, or adopts a specific tone for replies.

## Project Structure

- `app.py`: The main application entry point, handling the UI and state management.
- `services/`:
    - `llm_services.py`: The core logic for interacting with the Groq LLM.
    - `utils.py`: Helper functions for robust parsing and data formatting.
    - `data_manager.py`: Handles reading and writing to the JSON data files.
- `data/`: Local JSON storage.
