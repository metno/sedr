import schemathesis


@schemathesis.hook
def before_generate_query(context, strategy):
    # Only even 'id' values during test generation
    return strategy.filter(lambda x: x["id"] % 2 == 0).map(
        lambda x: {"id": x["id"] ** 2}
    )