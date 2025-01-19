import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from google import genai
from google.genai import types
import telegramify_markdown
from telegramify_markdown.customize import markdown_symbol
from telegramify_markdown.interpreters import BaseInterpreter, MermaidInterpreter
from telegramify_markdown.type import ContentTypes
import time
from src.ai_agents import Agent

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_API_KEY")
API_KEY = os.getenv("GEMINI_API")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting the Telegram bot...")

# Customizing global rendering options
markdown_symbol.head_level_1 = "📌"
markdown_symbol.link = "🔗"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome to the AI-powered Telegram Bot! Use /help to see available commands.')
    logger.info("User started the bot.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Available commands:\n/start - Welcome message\n/help - List commands\n/generate <text> - Generate content.')
    logger.info("User requested help.")

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    agent = Agent()
    content = agent.generate_content()

    boxs = await telegramify_markdown.telegramify(
        content=content["content_md"],
        interpreters_use=[BaseInterpreter(), MermaidInterpreter()],
        latex_escape=True,
        normalize_whitespace=True,
        max_word_count=4090
    )
    for item in boxs:
        logger.info("Sent item!")
        time.sleep(0.2)
        try:
            if item.content_type == ContentTypes.TEXT:
                await update.message.reply_text(item.content, parse_mode="MarkdownV2")
            elif item.content_type == ContentTypes.PHOTO:
                await update.message.reply_photo((item.file_name, item.file_data), item.caption, parse_mode="MarkdownV2")
            elif item.content_type == ContentTypes.FILE:
                await update.message.reply_document((item.file_name, item.file_data), caption=item.caption, parse_mode="MarkdownV2")
        except Exception as e:
            logger.error(f"Error with {item}")
            await update.message.reply_text(f"Error with {item}")
    logger.info(f"Generated content for user")

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("generate", generate))

    logger.info("Bot is polling for updates...")
    application.run_polling()

if __name__ == '__main__':
    main()