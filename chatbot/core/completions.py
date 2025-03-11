import asyncio
import json
import logging
import time

from openai import AsyncOpenAI

from chatbot.core.config import config
from chatbot.core.utils import tools_func, tools_json

logger = logging.getLogger(__name__)


class Completions:
    def __init__(
        self,
        name="DTeam_Bot",
        model="radiance",
    ):
        self.client = AsyncOpenAI(
            api_key=config.AVANGENIO_API_KEY,
            base_url="https://apigateway.avangenio.net",
        )
        self.name = name
        self.model = model
        self.error_response = "Ha ocurrido un error, realice la consulta más tarde"

    async def submit_message(self, messages, user_number=None):
        last_time = time.time()
        logger.debug(f"Runnung {self.name} with {len(tools_func)} functions")
        while True:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools_json,
            )
            if response.choices[0].message.tool_calls:
                await self.run_tools(messages, response, user_number)
                continue

            break

        ans = response.choices[0].message.content
        logger.info(f"{self.name}: {ans}")
        logger.info(f"Performance de {self.name}: {time.time() - last_time}")
        return ans

    async def run_tools(self, messages, response, user_number) -> None:
        tools = response.choices[0].message.tool_calls
        logger.info(f"{len(tools)} tools need to be called!")
        messages.append(response.choices[0].message)  # Peticion de tools

        tasks = []
        for tool in tools:
            function_name = tool.function.name
            function_args = json.loads(tool.function.arguments)
            logger.info(function_name)
            logger.info(function_args)
            function_to_call = tools_func[function_name]

            if user_number:
                tasks.append(function_to_call(**function_args, user_number=user_number))
            else:
                tasks.append(function_to_call(**function_args))

        results = await asyncio.gather(*tasks)
        for tool, function_response in zip(tools, results):
            if isinstance(function_response, Exception):
                logger.error(f"{tool.function.name}: {function_response}")
                function_response = self.error_response
            else:
                logger.info(f"{tool.function.name}: {function_response[:50]}")

            messages.append(
                {
                    "tool_call_id": tool.id,
                    "role": "tool",
                    "name": tool.function.name,
                    "content": function_response,
                }
            )
