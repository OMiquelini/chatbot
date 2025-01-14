import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import PyPDF2

app = Flask(__name__)

# OpenAI API Key
openai.api_key = "your_openai_api_key"

# Load PDF Content
def load_pdf_content(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            content = ""
            for page in reader.pages:
                content += page.extract_text()
            return content
    except Exception as e:
        return f"Error reading PDF: {e}"

# Preload the PDF content
PDF_PATH = "path_to_your_pdf_file.pdf"
pdf_content = load_pdf_content(PDF_PATH)

# Webhook for WhatsApp
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    incoming_msg = request.values.get('Body', '').strip()
    response = MessagingResponse()
    reply = response.message()

    if not pdf_content:
        reply.body("Sorry, the PDF content could not be loaded.")
        return str(response)

    try:
        # Use GPT API to answer based on the PDF content
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"You are an assistant who answers only based on the following document: {pdf_content}"},
                {"role": "user", "content": incoming_msg},
            ],
        )
        bot_reply = gpt_response['choices'][0]['message']['content']
    except Exception as e:
        bot_reply = "Sorry, I couldn't process that. Please try again later."

    reply.body(bot_reply)
    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
