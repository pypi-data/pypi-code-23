# codign: utf-8
import logging
logger = logging.getLogger(__name__)


def _calculate_node_score(node):
    scores = list()
    if not node:
        logger.info('empty node, returning 0')
        return (0, 0, )

    children = node.get_children()
    if len(children) <= 0:
        total = node.weight
        if node.status.is_closing_status:
            done = node.weight
        else:
            done = 0
        return (done, total, )
    else:
        for child in children:
            scores.append(_calculate_node_score(child))

        closed = sum([s[0] for s in scores])
        total = sum([s[1] for s in scores])
        return (closed, total, )


def calculate_node_score(node):
    score = _calculate_node_score(node)
    total = score[1]
    if total == 0:
        total = 1
    return float(score[0]) / float(total)


def calculate_project_score(project):

    """
    Calculates a projects score, based
    on how many open/closed tasks it has
    """

    if not project:
        raise ValueError('project is required to calculate score')
    root_tasks = project.root_tasks.all()
    if root_tasks.count() <= 0:
        return 0.0

    scores = [calculate_node_score(r) for r in root_tasks]
    return sum(scores) / float(len(scores))
