"""新手引导：前置依赖、跳过条件、请求幂等与步骤顺序。"""


class Tutorial:
    """引导步骤状态机。"""

    def __init__(self, steps):
        self.steps = [dict(step) for step in steps]
        self.by_id = {step["id"]: step for step in self.steps}
        self.done = set()
        self.skipped = set()
        self.pending = set()
        self.applied = set()
        self.scanned = 0

    def activate(self, step_id, req_id):
        """触发一个引导步骤。"""
        step = self.by_id.get(step_id)
        if step is None:
            return False
        if req_id in self.applied:
            return False
        if step_id in self.done or step_id in self.skipped:
            return False
        requires = step.get("requires") or ()
        for dep in requires:
            self.scanned += 1
            if dep not in self.done and dep not in self.skipped:
                self.pending.add(step_id)
                return False
        self.applied.add(req_id)
        self.pending.discard(step_id)
        if step.get("skip_flag"):
            self.skipped.add(step_id)
        else:
            self.done.add(step_id)
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
        resolved = self.done | self.skipped
        return [step["id"] for step in self.steps if step["id"] in resolved]

    def scanned_count(self):
        return self.scanned
