from flask import Blueprint
from simulation.store import Store

bp = Blueprint('stats', __name__, url_prefix='')

@bp.route("/", methods=['GET'])
def statsFunc():
    stats = {
        "all_tasks": Store.getTotalTaskCount(),
        "success_tasks": Store.getSuccessTaskCount(),
        "after_deadline_tasks": Store.getStartedFailedTaskCount(),
        "failed_tasks": Store.getStartedFailedTaskCount(),
        "tasks_to_execute": Store.getTasksToExecuteCount(),
        "incomplete_tasks": Store.getIncompleteTasksCount(),
        "finished_tasks": Store.getSuccessTaskCount(),
        #"maxTaskCount": config.MAX_TASK_COUNT
    }
    #print("incomplete_tasks", Store.getIncompleteTasksCount())
    return stats