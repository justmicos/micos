"""absorb-osp — Data Models"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class Depth(str, Enum):
    """Absorption depth levels."""
    L1 = "L1"  # Knowledge
    L2 = "L2"  # Tool
    L3 = "L3"  # Service
    L4 = "L4"  # Plugin
    L5 = "L5"  # Deep Integration


class Status(str, Enum):
    """Project absorption status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BUILT = "built"
    ONLINE = "online"
    INSTALLED = "installed"
    REJECTED = "rejected"
    DEFERRED = "deferred"
    FAILED = "failed"


class ClassifyDecision(str, Enum):
    """Classification merge decision."""
    MERGE = "MERGE"
    SUPERSEDE = "SUPERSEDE"
    ENHANCE = "ENHANCE"
    STANDALONE = "STANDALONE"


@dataclass
class JudgeScore:
    """5-dimension judge scorecard."""
    capability_fit: int = 3
    feasibility: int = 3
    interface_compat: int = 3
    maintenance_cost: int = 3
    security_risk: int = 3

    @property
    def total(self) -> float:
        """Calculate weighted total score."""
        return (
            self.capability_fit * 0.30
            + self.feasibility * 0.25
            + self.interface_compat * 0.20
            + self.maintenance_cost * 0.15
            + self.security_risk * 0.10
        )

    @property
    def decision(self) -> str:
        """Judge decision based on total score."""
        t = self.total
        if t >= 4.0:
            return "Strong absorb"
        elif t >= 3.0:
            return "Absorb"
        elif t >= 2.0:
            return "Conditional absorb"
        else:
            return "Reject"

    @property
    def suggested_depth(self) -> Depth:
        """Suggested absorption depth based on score."""
        t = self.total
        if t >= 4.0:
            return Depth.L5
        elif t >= 3.0:
            return Depth.L3
        elif t >= 2.0:
            return Depth.L1
        else:
            return Depth.L1


@dataclass
class ProjectInfo:
    """GitHub project metadata."""
    github_url: str
    name: str
    stars: int = 0
    license_type: str = "Unknown"
    description: str = ""
    language: str = ""
    last_commit: str = ""
    contributors: int = 0
    open_issues: int = 0
    has_cli: bool = False
    has_api: bool = False
    has_library: bool = False
    has_web_ui: bool = False


@dataclass
class AbsorbedProject:
    """Record of an absorbed project."""
    name: str
    github_url: str
    depth: Depth
    status: Status = Status.PENDING
    license_type: str = ""
    judge_score: float = 0.0
    classify_decision: ClassifyDecision = ClassifyDecision.STANDALONE
    absorb_date: str = ""
    local_path: str = ""
    port: Optional[int] = None
    integration_targets: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class WorkflowStep:
    """A single step in the absorption workflow."""
    number: int
    name: str
    status: str = "pending"  # pending | running | passed | failed | skipped
    output: str = ""
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def start(self):
        """Mark step as running."""
        self.status = "running"
        self.started_at = datetime.now()

    def complete(self, status: str = "passed", output: str = ""):
        """Mark step as completed."""
        self.status = status
        self.output = output
        self.completed_at = datetime.now()


@dataclass
class WorkflowResult:
    """Result of a complete absorption workflow run."""
    steps: list[WorkflowStep] = field(default_factory=list)
    project: Optional[ProjectInfo] = None
    report_path: str = ""
    success: bool = False
    error: str = ""

    def _add(self, number: int, name: str) -> WorkflowStep:
        """Add a new step to the result and return it."""
        step = WorkflowStep(number=number, name=name)
        self.steps.append(step)
        return step
