from .conditional_operator import ConditionalOperatorAnalysis
from .locals import LocalsAnalysis


class Analysis:
    def __init__(self):
        self._conditional_operator_analysis = ConditionalOperatorAnalysis()
        self._locals_analysis = LocalsAnalysis()

    def on_transformation_finished(self):
        self._conditional_operator_analysis.on_transformation_finished()
        self._locals_analysis.on_transformation_finished()

    def process_assignment(self, *args, **kwargs):
        self._locals_analysis.process_assignment(*args, **kwargs)

    def process_access(self, *args, **kwargs):
        self._locals_analysis.process_access(*args, **kwargs)

    def process_binary(self, *args, **kwargs):
        self._locals_analysis.process_binary(*args, **kwargs)

    def process_reinterpret(self, *args, **kwargs):
        self._locals_analysis.process_reinterpret(*args, **kwargs)

    def process_local(self, *args, **kwargs):
        self._conditional_operator_analysis.process_local(*args, **kwargs)
        self._locals_analysis.process_local(*args, **kwargs)

    def process_stackvar(self, *args, **kwargs):
        self._conditional_operator_analysis.process_stackvar(*args, **kwargs)

    def process_arguments(self, *args, **kwargs):
        self._locals_analysis.process_arguments(*args, **kwargs)

    def process_memory_copy(self, *args, **kwargs):
        self._locals_analysis.process_memory_copy(*args, **kwargs)

    def transform_block_instructions(self, *args, **kwargs):
        self._conditional_operator_analysis.transform_block_instructions(
            *args, **kwargs)

    def collect_stack_accesses(self, *args, **kwargs):
        self._locals_analysis.collect_stack_accesses(*args, **kwargs)

    def fill_stack_variables(self, *args, **kwargs):
        return self._locals_analysis.fill_stack_variables(*args, **kwargs)
