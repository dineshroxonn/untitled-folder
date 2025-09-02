
import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InternalError,
    InvalidParamsError,
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError

from .agent import CarDiagnosticAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CarDiagnosticAgentExecutor(AgentExecutor):
    """Car Diagnostic AgentExecutor."""

    def __init__(self, agent: CarDiagnosticAgent):
        self.agent = agent

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        if not context.message or not context.message.parts:
            raise ServerError(error=InvalidParamsError("No message parts found."))

        query = context.get_user_input()
        if not query:
            raise ServerError(error=InvalidParamsError("No query found in message parts."))

        task = context.current_task or new_task(context.message)
        await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        full_response = ""
        try:
            async for chunk in self.agent.stream(query):
                if chunk:
                    full_response += chunk
                    await updater.update_status(
                        TaskState.working,
                        new_agent_text_message(
                            chunk,
                            task.context_id,
                            task.id,
                        ),
                    )
            
            # Once streaming is done, add the full response as the final artifact
            if full_response:
                await updater.add_artifact(
                    [Part(root=TextPart(text=full_response))],
                    name="diagnosis_report",
                )

            await updater.complete()

        except Exception as e:
            logger.error(f"An error occurred while streaming the response: {e}")
            await updater.fail(message=str(e))
            raise ServerError(error=InternalError()) from e

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise ServerError(error=UnsupportedOperationError())


def get_agent_executor() -> AgentExecutor:
    agent = CarDiagnosticAgent()
    return CarDiagnosticAgentExecutor(agent)
