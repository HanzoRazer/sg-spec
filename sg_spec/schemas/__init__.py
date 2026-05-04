"""
sg-spec Contract Schemas

Canonical source of truth for Smart Guitar data models.

Usage:
    # Instrument specs
    from sg_spec.schemas import SmartGuitarSpec, SmartGuitarInfo
    from sg_spec.schemas.sandbox_schemas import ModelVariant, CavityPlan

    # Groove layer
    from sg_spec.schemas.groove_layer import GrooveProfileV1, GrooveControlIntentV1

    # Generation bus (request/result)
    from sg_spec.schemas.generation import GenerationRequest, GenerationResult

    # Clip bundle
    from sg_spec.schemas.clip_bundle import ClipBundle, ClipRunLog

    # Technique sidecar
    from sg_spec.schemas.technique_sidecar import TechniqueSidecar, TechniqueAnnotation

    # Adaptive feedback (Phase 5)
    from sg_spec.schemas.adaptive_feedback import AdaptiveFeedbackV1, DiagnosisCode

    # Practice assignment (Phase 5.2)
    from sg_spec.schemas.practice_assignment import PracticeAssignmentDoc

    # Feedback vocabulary (Phase 5.3)
    from sg_spec.schemas.feedback_vocabulary import (
        FeedbackDomain, FeedbackSeverity, FeedbackRenderHint, FeedbackActionType
    )

    # Coach finding contracts (Phase 5.3)
    from sg_spec.schemas.coach_finding import (
        CoachFindingContract, FindingEvidenceContract,
        SuggestedFeedbackAction, TargetSpan
    )

    # Action mapping (Sprint 4)
    from sg_spec.schemas.action_mapping import (
        ActionMapping, RecommendedAction, ActionRecommendationSet
    )

    # User feedback loop (Sprint 5)
    from sg_spec.schemas.user_feedback import (
        UserFeedbackResponseType, PracticeOutcome,
        UserFeedbackEvent, LearningSignal
    )
"""

from .smart_guitar import *
from .sandbox_schemas import *
from .groove_layer import *
from .clip_bundle import *
from .technique_sidecar import *
from .adaptive_feedback import *
from .practice_assignment import *
from .feedback_vocabulary import *
from .coach_finding import *
from .coach_schemas import *
from .action_mapping import *
from .user_feedback import *
from .generation import *  # Must be last (depends on coach_schemas)

__version__ = "1.8.0"
