import openai
import google.auth
from googleapiclient.discovery import build
import time

# OpenAI API Key
openai.api_key = "your_openai_api_key"

# YouTube API Setup
def get_authenticated_service():
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/youtube.force-ssl"])
    return build("youtube", "v3", credentials=credentials)

# Get Live Chat ID
def get_live_chat_id(youtube):
    live_broadcasts = youtube.liveBroadcasts().list(part="snippet", broadcastStatus="active").execute()
    if live_broadcasts["items"]:
        return live_broadcasts["items"][0]["snippet"]["liveChatId"]
    return None

# Fetch Messages and Respond
def chat_bot(youtube, live_chat_id):
    next_page_token = None
    while True:
        try:
            # Get live chat messages
            chat_response = youtube.liveChatMessages().list(
                liveChatId=live_chat_id, part="snippet,authorDetails", pageToken=next_page_token
            ).execute()

            for item in chat_response.get("items", []):
                user_message = item["snippet"]["displayMessage"]
                user_name = item["authorDetails"]["displayName"]

                # Check if the message starts with -b
                if not user_message.startswith("-b"):
                    continue  # Ignore the message

                # Remove the prefix before sending to GPT
                user_message = user_message[2:].strip()
                print(f"{user_name}: {user_message}")

                # Process with GPT
                gpt_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": user_message}]
                )
                bot_message = gpt_response["choices"][0]["message"]["content"]
                print(f"Bot: {bot_message}")

                # Send response back to chat
                youtube.liveChatMessages().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "liveChatId": live_chat_id,
                            "type": "textMessageEvent",
                            "textMessageDetails": {"messageText": bot_message},
                        }
                    },
                ).execute()

            # Update page token for next call
            next_page_token = chat_response.get("nextPageToken")
            time.sleep(5)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    youtube = get_authenticated_service()
    live_chat_id = get_live_chat_id(youtube)
    if live_chat_id:
        chat_bot(youtube, live_chat_id)
    else:
        print("No active live chat found.")
