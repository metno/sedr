import click
import schemathesis
from schemathesis.cli.handlers import EventHandler
from schemathesis.cli.context import ExecutionContext
from schemathesis.hooks import HookContext
from schemathesis.runner import events
from typing import List
import pprint
import json
import sedr.util as util
import sedr.edreq11 as edreq


@schemathesis.hook
def after_call(context, case, response):
    """Hook runs after any call to the API."""
    if response.request:
        # Log calls with status
        # print(
        #     f"after_call {'OK' if response.ok else 'ERR'} "
        #     + f"{response.request.path_url} {response.text[0:150]}"
        # )

        if response.request.path_url == "/":
            # test_edr_landingpage
            """Test that the landing page contains required elements."""
            spec_ref = "https://docs.ogc.org/is/19-072/19-072.html#_7c772474-7037-41c9-88ca-5c7e95235389"
            try:
                landingpage_json = response.json()
                landing, landing_message = util.parse_landing_json(landingpage_json)
                if not landing:
                    raise AssertionError(
                        f"Landing page is missing required elements. See <{spec_ref}> for more info. {landing_message}"
                    )

                print("Landingpage %s tested OK", response.url)
            except json.decoder.JSONDecodeError as e:
                print(
                    f"Landing page is not valid JSON, other formats are not tested yet., {e}"
                )


        if response.request.path_url == "/conformance":
            # def test_edr_conformance(case):
            """Test /conformance endpoint."""
            conformance_json = response.json()

            if "conformsTo" not in conformance_json:
                spec_ref = "https://docs.ogc.org/is/19-072/19-072.html#_4129e3d3-9428-4e91-9bfc-645405ed2369"
                raise AssertionError(
                    f"Conformance page /conformance does not contain a conformsTo attribute. See {spec_ref} for more info."
                )

            resolves, resolves_message = util.test_conformance_links(
                jsondata=conformance_json["conformsTo"]
            )
            if not resolves:
                raise AssertionError(resolves_message)

            requirementA2_2_A5, requirementA2_2_A5_message = edreq.requirementA2_2_A5(
                jsondata=conformance_json["conformsTo"]
            )
            if not requirementA2_2_A5:
                raise AssertionError(requirementA2_2_A5_message)

            requirementA2_2_A7, requirementA2_2_A7_message = edreq.requirementA2_2_A7(
                response.raw.version
            )
            if not requirementA2_2_A7:
                raise AssertionError(requirementA2_2_A7_message)

            requirementA11_1, requirementA11_1_message = edreq.requirementA11_1(
                jsondata=conformance_json["conformsTo"]
            )
            if not requirementA11_1:
                raise AssertionError(requirementA11_1_message)

            print("Conformance %s tested OK", response.url)


# class SimpleHandler(EventHandler):
#     def handle_event(self, context, event):
#         print(event.__class__)

#         if isinstance(event, events.AfterProbing):
#             print("AfterProbing event:")
#             pprint.pp(event)

#         if isinstance(event, events.Finished):
#             print("Finished event:")
#             pprint.pp(event)


# @schemathesis.hook
# def after_init_cli_run_handlers(
#     context: HookContext,
#     handlers: List[EventHandler],
#     execution_context: ExecutionContext,
# ) -> None:
#     handlers[:] = [SimpleHandler()]
