import datetime
from typing import Optional

class Finalizer:
    """Handles the completion of a run, including PR creation and reporting."""

    def __init__(self, git_manager, commenter):
        self.git_manager = git_manager
        self.commenter = commenter

    def finalize_success(self, context: Any, result_summary: str, repo_full_name: str):
        """Closes a successful run."""
        print(f"Finalizing success for run {context.run_id}")

        # 1. Create PR from WIP branch
        self.git_manager.create_pull_request(
            head=context.wip_branch,
            base="main",
            title=f"AI Fix: {context.user_request[:50]}",
            body=f"Automated changes for run {context.run_id}.\n\n{result_summary}"
        )

        # 2. Update progress comment to Completed
        self.commenter.upsert_progress_comment(
            repo_full_name=repo_full_name,
            item_id=context.item_id,
            status="Completed",
            message=f"Task finished successfully!\n\n{result_summary}"
        )

    def finalize_failure(self, context: Any, reason: str, repo_full_name: str):
        """Closes a failed run."""
        print(f"Finalizing failure for run {context.run_id}: {reason}")

        self.commenter.upsert_progress_comment(
            repo_full_name=repo_full_name,
            item_id=context.item_id,
            status="Failed",
            message=f"Run failed with reason: {reason}\n\nRecovery hint: Please check logs or try /ai again."
        )
