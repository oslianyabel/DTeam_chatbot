import logging
import uuid

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from chatbot.core import notifications
from chatbot.core.completions import Completions
from chatbot.core.config import config
from chatbot.loggin_conf import configure_loggin
from chatbot.models.message import Message
from chatbot.core.utils import prompt

configure_loggin()
logger = logging.getLogger(__name__)
logger.debug("="*200)
app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)
empty_chat = [{"role": "system", "content": prompt}]
bots: dict[str, object] = {}


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)


def create_thread():
    return str(uuid.uuid4())


@app.post("/chat", response_model=Message)
async def odoo_reply(request: Message):
    user_msg = request.message
    thread_id = request.thread_id

    try:
        if not user_msg or not thread_id:
            logger.info("Creando nuevo hilo")
            thread_id = create_thread()
            bots[thread_id] = bot = Completions(
                messages=empty_chat,
            )
            if not user_msg:
                logger.info("Mensaje de bienvenida")
                ans = await bot.submit_message("Hola, como puedes ayudarme?")
            else:
                logger.debug(f"User: {user_msg}")
                ans = await bot.submit_message(user_msg)
        else:
            logger.debug(f"User: {user_msg}")
            if thread_id not in bots:
                bots[thread_id] = Completions(
                    messages=empty_chat,
                )
                logger.info(f"El hilo {thread_id} está vacío, se iniciará nuevo chat en él")
            bot = bots[thread_id]
            logger.info(f"chat con {len(bot.messages)} mensajes")
            ans = await bot.submit_message(user_msg)

    except Exception as exc:
        manage_exc(user_msg, exc)

    return {"thread_id": thread_id, "message": ans}


def manage_exc(user_msg, exc):
    logger.error(exc)
    notifications.send_email(
        config.MY_EMAIL,
        "Error while running assistant",
        f"User msg: {user_msg}\nError: {exc}",
    )
    error_msg = f"Ha ocurrido un error. Consulte más tarde. Error: {exc}"
    raise HTTPException(500, error_msg)
