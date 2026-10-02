"""新手引导：前置依赖、跳过条件、请求幂等与步骤顺序。

缺陷：不检查前置依赖、跳过条件不生效、同一个请求重复生效、
进度按完成顺序而不是定义顺序、每次触发扫描全部步骤。
"""


class Tutorial:
    """引导步骤状态机。"""

    def __init__(self, steps):
        self.steps = [dict(step) for step in steps]
        self.by_id = {step["id"]: step for step in self.steps}
        self.done = set()
        self.skipped = set()
        self.pending = set()
        self.applied = set()
        self.order = []
        self.scanned = 0

    def activate(self, step_id, req_id):
        """触发一个引导步骤。"""
        self.scanned += len(self.steps)
        step = self.by_id.get(step_id)
        if step is None:
            return False
        self.applied.add(req_id)
        self.done.add(step_id)
        self.order.append(step_id)
        return True

    def complete(self, step_id, req_id):
        return self.activate(step_id, req_id)

    def is_done(self, step_id):
        return step_id in self.done

    def skipped_list(self):
        return sorted(self.skipped)

    def pending_list(self):
        return sorted(self.pending)

    def progress(self):
        """按定义顺序返回已完成或已跳过的步骤。"""
        return list(self.order)

    def scanned_count(self):
        return self.scanned
