from typing import List, Optional
from .state_machine import StateMachine, RunStatus
from .context import RunContext

class Pipeline:
    """Orchestrates the flow from trigger to finalization."""

    def __init__(self, github_client=None):
        self.github = github_client

    def process_request(self, context: RunContext):
        """Main entry point for processing a request."""
        try:
            self._transition(context, RunStatus.CLASSIFYING)
            self._classify(context)

            self._transition(context, RunStatus.RISK_ASSESSING)
            self._assess_risk(context)

            self._transition(context, RunStatus.PLANNING)
            self._plan(context)

            self._transition(context, RunStatus.IMPLEMENTING)
            self._implement(context)

            self._transition(context, RunStatus.FINALIZING)
            self._finalize(context)

            self._transition(context, RunStatus.COMPLETED)
        except Exception as e:
            print(f"Pipeline failed: {e}")
            self._transition(context, RunStatus.FAILED)
            raise

    def _transition(self, context: RunContext, next_status: RunStatus):
        if not StateMachine.validate_transition(context.status, next_status):
            raise RuntimeError(f"Invalid transition from {context.status} to {next_status}")

        print(f"Transitioning run {context.run_id} from {context.status} to {next_status}")
        context.status = next_status

    def _classify(self, context: RunContext):
        print(f"Classifying request for run {context.run_id}...")
        # To be implemented in Phase 2
        pass

    def _assess_risk(self, context: RunContext):
        print(f"Assessing risk for run {context.run_id}...")
        # To be implemented in Phase 2
        pass

    def _plan(self, context: RunContext):
        print(f"Planning solution for run {context.run_id}...")
        # In Phase 3: Use Agent backend to generate a plan
        pass

    def _implement(self, context: RunContext):
        print(f"Implementing solution for run {context.run_id}...")
        # In Phase 3: Execute agent implementation and update progress
        pass


    def _finalize(self, context: RunContext):
        print(f"Finalizing run {context.run_id}...")
        # Phase 4: Create PR and post final summary
        pass

