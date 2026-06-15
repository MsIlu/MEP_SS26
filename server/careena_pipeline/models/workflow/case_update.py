from careena_pipeline.models.workflow.message_update import MessageUpdate


class CaseUpdate(MessageUpdate):
    """
    Backward-compatible alias while the pipeline shifts from CaseUpdate to the
    more explicit MessageUpdate concept.
    """
