from flask import Blueprint, Flask
from Store import Store
import config

bp = Blueprint('stats', __name__, url_prefix='')

@bp.route("/", methods=['GET'])
def statsFunc():
    stats = {
        "all_tasks": Store.getTotalTaskCount(),
        "success_tasks": Store.getSuccessTaskCount(),
        "failed_tasks": Store.getStartedFailedTaskCount(),
        "tasks_to_execute": Store.getTasksToExecuteCount(),
        "incomplete_tasks": Store.getIncompleteTasksCount(),
        "finished_tasks": Store.getSuccessTaskCount(),
        "maxTaskCount": config.MAX_TASK_COUNT
    }
    
    return stats