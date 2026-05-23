"""
absorb-osp — Open Source Project Absorption Workflow Engine

A systematic 12-step closed-loop flywheel for evaluating, absorbing,
internalizing, and evolving open-source projects into your AI agent ecosystem.
"""

__version__ = "2.0.0"
__author__ = "justmicos"
__license__ = "MIT"

from .lib.models import (
    AbsorbedProject,
    ClassifyDecision,
    Depth,
    JudgeScore,
    ProjectInfo,
    Status,
    WorkflowResult,
    WorkflowStep,
)
