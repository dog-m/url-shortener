from backend.core.tasks import periodic_task

#


@periodic_task(100.0)
async def task_event_upload() -> None:
    print('[~] TODO: event sync task')

