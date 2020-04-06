class AbstractSolver:
    def set_log_strategy(self, log):
        self.log_result = []
        if log:
            self.may_reset_log = lambda: self.log_result.clear()
            self.may_log = lambda states: self.log_result.append(states)
        else:
            self.may_reset_log = lambda: None
            self.may_log = lambda *args: None

    def set_engine_strategy(self, engine_name):
        pass

    def set_parameters(self):
        pass

    def set_instance(self, instance):
        self.may_reset_log()
        self.instance = instance

    def run(self):
        raise NotImplementedError

    def retrieve_solution(self):
        raise NotImplementedError
