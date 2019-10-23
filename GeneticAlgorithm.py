class schedule_genom:
    task_plan = None
    penalty = None

    def __init__(self, task_plan, penalty):
        """
        :param task_plan こなすタスクのリスト
            e.g.) [3, 2, 1, 0, 1, 2, 3, 2, 2, 3, 1]
        :param penalty 評価関数の値
        """
        self.task_plan = task_plan
        self.penalty = penalty

    def GetPlan(self):
        return self.task_plan

    def GetPenalty(self):
        return self.penalty
    
    def SetPlan(self, task_plan):
        self.task_plan = task_plan

    def SetPenalty(self, penalty):
        self.penalty = penalty
