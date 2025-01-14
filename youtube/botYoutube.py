import openai
import google.auth
from googleapiclient.discovery import build
import time
import PyPDF2

# Function to load and extract text from the PDF
def load_pdf_content(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            content = ""
            for page in reader.pages:
                content += page.extract_text()
            return content
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

# Load the PDF content once
PDF_PATH = "path_to_your_pdf_file.pdf"
pdf_content = load_pdf_content(PDF_PATH)

if pdf_content:
    print("PDF content successfully loaded.")
else:
    print("Failed to load PDF content.")

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

                # Ensure PDF content is loaded
                if not pdf_content:
                    print("The reference document is unavailable.")
                    continue

                print(f"{user_name}: {user_message}")

                # Process with GPT using the PDF content as context
                gpt_response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": f"Answer based on the following document: {pdf_content}"},
                        {"role": "user", "content": user_message}
                    ]
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
