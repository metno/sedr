import click
import schemathesis
from schemathesis.cli.handlers import EventHandler
from schemathesis.cli.context import ExecutionContext
from schemathesis.hooks import HookContext
from schemathesis.runner import events
from typing import List
import pprint


class SimpleHandler(EventHandler):
    def handle_event(self, context, event):
        # pprint.pp(event)
        if isinstance(event, events.Finished):
            print("Done!")
            pprint.pp(event)


@schemathesis.hook
def after_init_cli_run_handlers(
    context: HookContext,
    handlers: List[EventHandler],
    execution_context: ExecutionContext,
) -> None:
    handlers[:] = [SimpleHandler()]
