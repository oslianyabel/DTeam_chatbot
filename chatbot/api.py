import logging
import uuid

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from chatbot.core import notifications
from chatbot.core.completions import Completions
from chatbot.core.config import config
from chatbot.core.utils import prompt
from chatbot.loggin_conf import configure_loggin
from chatbot.models.message import Message

configure_loggin()
logger = logging.getLogger(__name__)
logger.debug("=" * 200)
app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)
empty_chat = [{"role": "system", "content": prompt}]
chats: dict[str, list] = {}
bot = Completions()


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)


def create_thread():
    logger.info("Creando nuevo hilo")
    thread_id = str(uuid.uuid4())
    chats[thread_id] = empty_chat
    return thread_id


def add_msg(thread_id: str, role: str, msg: str):
    logger.debug(f"{role}: {msg}")
    chats[thread_id].append(
        {
            "role": role,
            "content": msg,
        }
    )


@app.post("/chat", response_model=Message)
async def odoo_reply(request: Message):
    user_msg = request.message
    thread_id = request.thread_id

    try:
        if not user_msg or not thread_id:
            thread_id = create_thread()
            if not user_msg:
                user_msg = "Hola, como puedes ayudarme?"

        elif thread_id not in chats:
            logger.info(f"El hilo {thread_id} está vacío, se iniciará nuevo chat en él")
            chats[thread_id] = empty_chat

        logger.info(f"chat con {len(chats[thread_id])} mensajes")
        add_msg(thread_id, "user", user_msg)
        ans = await bot.submit_message(chats[thread_id])
        add_msg(thread_id, "assistant", ans)

    except Exception as exc:
        manage_exc(user_msg, exc)

    return {"thread_id": thread_id, "message": ans}


def manage_exc(user_msg, exc):
    logger.error(exc)
    notifications.send_email(
        config.MY_EMAIL,
        "Error while running completions",
        f"User msg: {user_msg}\nError: {exc}",
    )
    error_msg = f"Ha ocurrido un error. Consulte más tarde. Error: {exc}"
    raise HTTPException(500, error_msg)
