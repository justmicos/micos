"""absorb-osp — Workflow Engine (12-step closed-loop flywheel)"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from .analyzer import analyze_github_url, detect_tech_stack
from .models import (
    ClassifyDecision,
    Depth,
    JudgeScore,
    ProjectInfo,
    Status,
    WorkflowResult,
    WorkflowStep,
)
from .reporter import generate_analysis_report, generate_usage_log
from .scanner import scan_for_leaks, security_scan


class WorkflowEngine:
    """Executes the 12-step closed-loop absorption flywheel."""

    def __init__(self, absorbed_dir: Optional[str] = None):
        self.absorbed_dir = absorbed_dir or os.environ.get(
            "ABSORB_ABSORBED_DIR",
            str(Path.home() / ".claude" / "absorbed"),
        )
        self.skills_dir = os.environ.get(
            "ABSORB_SKILLS_DIR",
            str(Path.home() / ".claude" / "skills"),
        )
        self.projects_dir = os.environ.get(
            "ABSORB_PROJECTS_DIR",
            str(Path.home() / "projects"),
        )

    def run(self, github_url: str, judge_score: Optional[JudgeScore] = None) -> WorkflowResult:
        """Execute the full 12-step workflow for a GitHub URL.

        Args:
            github_url: The GitHub repository URL to absorb.
            judge_score: Optional pre-set judge score. Uses defaults if not provided.

        Returns:
            WorkflowResult with all step outcomes.
        """
        result = WorkflowResult(success=False)

        try:
            # Step 0: Trigger
            step = result._add(0, "Trigger")
            step.start()
            print(f"\n🎯 Step 0: Trigger — {github_url}")
            step.complete("passed")

            # Step 1: Triage
            step = result._add(1, "Triage")
            step.start()
            print("🔍 Step 1: Triage — <30s quick scan...")
            if "github.com" not in github_url:
                raise ValueError(f"Not a GitHub URL: {github_url}")
            step.complete("passed", "URL valid. Security redline check deferred to Step 3.")

            # Step 2: Verify
            step = result._add(2, "Verify")
            step.start()
            print("📋 Step 2: Verify — fetching GitHub metadata...")
            project = analyze_github_url(github_url)
            result.project = project
            print(f"   → {project.name}: {project.stars}★, license={project.license_type}")
            step.complete("passed", f"{project.stars}★, {project.license_type}")

            # Step 3: Evaluate
            step = result._add(3, "Evaluate")
            step.start()
            print("🔬 Step 3: Evaluate — architecture + security scan...")
            # Run security scan on the local clone path if available
            project_path = str(Path(self.projects_dir) / project.name)
            if Path(project_path).exists():
                sec = security_scan(project_path)
                tech = detect_tech_stack(project_path)
                eval_detail = (
                    f"Security: {sec['gate']}, "
                    f"Tech: {tech.get('language') or 'unknown'}"
                )
                print(f"   → {eval_detail}")
            else:
                eval_detail = "Local clone not found. Security scan deferred."
                print(f"   → {eval_detail}")
            step.complete("passed", eval_detail)

            # Step 4: Judge
            step = result._add(4, "Judge")
            step.start()
            print("📊 Step 4: Judge — scoring matrix...")
            score = judge_score or JudgeScore()
            print(f"   → Score: {score.total:.1f}/5.0 → {score.decision} → Depth: {score.suggested_depth.value}")
            step.complete("passed", f"Score: {score.total:.1f}/5.0 → {score.decision}")

            # Step 5: Classify
            step = result._add(5, "Classify")
            step.start()
            existing = self._find_existing(project.name)
            if existing:
                decision = ClassifyDecision.ENHANCE
                print(f"   → Found existing: '{existing}'. Decision: ENHANCE (merge into existing)")
            else:
                decision = ClassifyDecision.STANDALONE
                print(f"   → No duplicates found. Decision: STANDALONE (fresh absorption)")
            step.complete("passed", decision.value)

            # Step 6: Internalize
            step = result._add(6, "Internalize")
            step.start()
            print("📝 Step 6: Internalize — generating artifacts...")
            Path(self.absorbed_dir).mkdir(parents=True, exist_ok=True)
            report_path = generate_analysis_report(project, score, self.absorbed_dir)
            usage_log_path = generate_usage_log(project.name, project.github_url, self.absorbed_dir)
            result.report_path = report_path
            print(f"   → Analysis report: {report_path}")
            print(f"   → Usage log:       {usage_log_path}")
            step.complete("passed", f"Report: {report_path}")

            # Step 7: Load
            result._add(7, "Load").complete("skipped", "Requires: git clone + dependency install")

            # Step 8: Integrate
            result._add(8, "Integrate").complete("skipped", "Requires: agent skill config + proxy route")

            # Step 9: Verify
            result._add(9, "Verify").complete("skipped", "Requires: service health check")

            # Step 10: Sync
            result._add(10, "Sync").complete("pending", "Run: absorb-osp index to sync memory")

            # Step 11: Iterate
            result._add(11, "Iterate").complete("pending", "Usage log created. Manual tracking needed.")

            # Step 12: Evolve
            result._add(12, "Evolve").complete("skipped", "Quarterly consolidation review")

            result.success = True
            print(f"\n✅ Absorption workflow complete for '{project.name}'")
            print(f"   Report: {report_path}")

        except Exception as e:
            result.success = False
            result.error = str(e)
            print(f"\n❌ Workflow failed: {e}")

        return result

    def _find_existing(self, name: str) -> Optional[str]:
        """Check if a project with similar name already exists in INDEX.md.

        Uses word-boundary matching to avoid false partial matches.
        """
        index_file = Path(self.absorbed_dir) / "INDEX.md"
        if not index_file.exists():
            return None
        content = index_file.read_text(encoding="utf-8")
        # Word-boundary match: only match whole project names
        pattern = re.compile(r'\b' + re.escape(name.lower()) + r'\b')
        if pattern.search(content.lower()):
            return name
        return None

    def list_absorbed(self) -> list[dict]:
        """List all absorbed projects from INDEX.md.

        Parses the markdown table format:
        | Project | Type | Depth | Status | Date | Integration |
        """
        index_file = Path(self.absorbed_dir) / "INDEX.md"
        if not index_file.exists():
            return []

        projects = []
        content = index_file.read_text(encoding="utf-8")
        for line in content.split("\n"):
            line = line.strip()
            if not line.startswith("|"):
                continue
            # Skip header/separator rows
            if "---" in line or line.startswith("| Project"):
                continue
            parts = [p.strip() for p in line.split("|")]
            # parts[0] is empty (before first |), parts[1] is Project, etc.
            if len(parts) >= 6 and parts[1]:
                projects.append({
                    "name": parts[1],
                    "type": parts[2] if len(parts) > 2 else "",
                    "depth": parts[3] if len(parts) > 3 else "",
                    "status": parts[4] if len(parts) > 4 else "",
                    "date": parts[5] if len(parts) > 5 else "",
                })
        return projects
