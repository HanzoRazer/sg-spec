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

    # Practice assignment (Phase 5.2 + Sprint 9)
    from sg_spec.schemas.practice_assignment import (
        PracticeAssignmentDoc,
        PracticeAssignmentType, PracticeAssignmentStatus,
        AssembledPracticeAssignment, AssembledPracticeAssignmentSet
    )

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
        UserFeedbackEvent, LearningSignal, FeedbackCaptureRequest
    )

    # Learning aggregation (Sprint 5)
    from sg_spec.schemas.learning_aggregation import (
        ActionEffectivenessProfile, LearningSignalAggregateSet
    )

    # Learning store (Sprint 6)
    from sg_spec.schemas.learning_store import (
        LearningSignalQuery, LearningStoreStats
    )

    # Personalization (Sprint 7)
    from sg_spec.schemas.personalization import (
        PersonalizationBlendConfig, PersonalizedActionScore,
        PersonalizedRankingResult
    )

    # Drill resolution (Sprint 8)
    from sg_spec.schemas.drill_resolution import (
        DrillDifficulty, DrillReference,
        DrillResolutionRequest, DrillResolutionResult
    )

    # Assignment outcome (Sprint 10)
    from sg_spec.schemas.assignment_outcome import (
        AssignmentOutcomeEvent, AssignmentOutcomeCaptureRequest
    )

    # MIDI session input (Sprint 11)
    from sg_spec.schemas.midi_session import (
        MidiEventType, MidiNoteEvent,
        SessionInputMetadata, MidiSessionInput
    )

    # Practice review (Sprint 12)
    from sg_spec.schemas.practice_review import (
        PracticeTimelineEntry, SessionReview,
        PracticeProgressSummary, PracticeTimeline
    )

    # Goal tracking (Sprint 13)
    from sg_spec.schemas.goal_tracking import (
        GoalStatus, WeaknessTrend,
        WeaknessProgression, PracticeGoal, GoalProgressSummary
    )

    # Curriculum alignment (Sprint 14)
    from sg_spec.schemas.curriculum_alignment import (
        CurriculumContentType, CurriculumReference,
        CurriculumAlignmentRequest, CurriculumAlignmentResult
    )

    # Runtime pipeline (Sprint 15)
    from sg_spec.schemas.runtime_pipeline import RuntimeCoachingResult
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
from .learning_aggregation import *
from .learning_store import *
from .personalization import *
from .drill_resolution import *
from .assignment_outcome import *
from .midi_session import *
from .practice_review import *
from .goal_tracking import *
from .curriculum_alignment import *
from .runtime_pipeline import *
from .generation import *  # Must be last (depends on coach_schemas)

__version__ = "2.0.0"
