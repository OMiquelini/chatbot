from twitchio.ext import commands
import openai

# OpenAI API Key
openai.api_key = "your_openai_api_key"

# Twitch Bot Setup
bot = commands.Bot(
    token="your_twitch_oauth_token",
    client_id="your_client_id",
    nick="your_bot_username",
    prefix="!",
    initial_channels=["your_channel_name"]
)

@bot.event
async def event_ready():
    print(f"Bot is ready | Logged in as {bot.nick}")

@bot.event
async def event_message(message):
    # Ignore messages from the bot itself
    if message.author.name.lower() == bot.nick.lower():
        return

    user_message = message.content

    # Ignore messages that don't start with -b
    if not user_message.startswith("-b"):
        return

    print(f"{message.author.name}: {user_message}")

    # Process with GPT
    try:
        gpt_response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}]
        )
        bot_reply = gpt_response["choices"][0]["message"]["content"]
        await message.channel.send(bot_reply)
    except Exception as e:
        print(f"Error: {e}")
        await message.channel.send("Sorry, I couldn't process that!")

if __name__ == "__main__":
    bot.run()
