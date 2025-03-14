import logging
import uuid

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI, HTTPException
from fastapi.exception_handlers import http_exception_handler

from chatbot.core import notifications
from chatbot.core.completions import Completions
from chatbot.core.config import config
from chatbot.core.utils import prompt, test_tools_func, tools_json
from chatbot.loggin_conf import configure_loggin
from chatbot.models.message import MessageIn, MessageOut

configure_loggin()
logger = logging.getLogger(__name__)
logger.debug("=" * 200)
app = FastAPI()
app.add_middleware(CorrelationIdMiddleware)
empty_chat = [{"role": "system", "content": prompt}]
chats: dict[str, list] = {}
bot = Completions(
    api_key=config.AVANGENIO_API_KEY,
    name="DTeam_Bot",
    tools_json=tools_json,
    functions=test_tools_func,
)


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)


def create_chat_id():
    logger.info("Creando nuevo chat_id")
    chat_id = str(uuid.uuid4())
    chats[chat_id] = empty_chat.copy()
    return chat_id


def add_msg(chat_id: str, role: str, msg: str):
    chats[chat_id].append(
        {
            "role": role,
            "content": msg,
        }
    )


@app.post("/chat", response_model=MessageOut)
async def reply(request: MessageIn):
    if request.secret != config.SECRET:
        raise HTTPException(401, "Secret invalid")
    
    user_msg = request.message
    chat_id = request.chat_id
    try:
        if not user_msg or not chat_id:
            chat_id = create_chat_id()
            if not user_msg:
                user_msg = "Hola, como puedes ayudarme?"

        elif chat_id not in chats:
            logger.info(f"El chat {chat_id} está vacío")
            chats[chat_id] = empty_chat.copy()

        logger.info(f"chat con {len(chats[chat_id])} mensajes")
        add_msg(chat_id, "user", user_msg)
        ans = await bot.submit_message(chats[chat_id])
        add_msg(chat_id, "assistant", ans)

    except Exception as exc:
        manage_exc(user_msg, exc)

    return {"chat_id": chat_id, "message": ans, "interactions": len(chats[chat_id]) - 1}


def manage_exc(user_msg, exc):
    logger.error(exc)
    notifications.send_email(
        config.MY_EMAIL,
        "Error while running completions",
        f"User msg: {user_msg}\nError: {exc}",
    )
    error_msg = f"Ha ocurrido un error. Consulte más tarde. Error: {exc}"
    raise HTTPException(500, error_msg)
