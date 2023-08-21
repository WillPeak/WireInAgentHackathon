# Chatbot with OpenAI and Streamlit

## Description

This project is a specialized chatbot designed to engage with users regarding their intentions, goals, and desires. Built using OpenAI and Streamlit, the bot is tailored to understand user aspirations across different domains such as professional careers, personal relationships, health and fitness, and long-term life planning. The bot features a time-tracking mechanism and can ingest user chats with ease.

## Installation

1. Clone the repository or download the source code.
2. Install the necessary packages using the following command:

    ```bash
    pip install openai streamlit dotenv streamlit-autorefresh
    ```

## Configuration

1. Create a `.env` file in the root directory of the project.
2. Add the following environment variables to the `.env` file:

    ```env
    INTERVAL_TIME_MINUTES=<time interval in minutes>
    USERNAME=<your username>
    OPENAI_API_KEY=<your OpenAI API key>
    MODEL=<model name>
    ```

3. Optional: If using the Telegram integration, make sure to input your Telegram Bot Token and Chat ID in the sidebar within the application.

## Usage

1. Run the Streamlit application using the following command:

    ```bash
    streamlit run <filename.py>
    ```

2. The application will open in your web browser. You can then interact with the chatbot by typing your messages in the chat input box.
3. You can view and engage with the chatbot, and it will automatically update based on the time intervals set.

## Features

- **Real-time Engagement**: The bot automatically updates after specific intervals to keep the conversation going.
- **Ingestion of User Chats**: Chats are processed and ingested for later use or analysis.
- **Customizable Time Tracking**: You can customize the time intervals for automatic updates.
- **Secure Environment Configuration**: Utilizing the `.env` file ensures that sensitive information like API keys is securely handled.
- **Telegram Integration**: Optional feature to connect with a Telegram bot for additional functionalities.

## Support

For any questions or support, please refer to the documentation or contact the development team.

## License

Please include details about the license, if applicable.
