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

    # Practice dashboard (Sprint 17)
    from sg_spec.schemas.practice_dashboard import (
        DashboardMetricCard, DashboardWeaknessTrend,
        DashboardGoalCard, DashboardAssignmentSummary,
        DashboardPracticeFrequency, PracticeDashboardData
    )

    # Session playback (Sprint 18)
    from sg_spec.schemas.session_playback import (
        PlaybackEventType, PlaybackTimelineEvent,
        PlaybackFindingOverlay, PlaybackAssignmentReference,
        SessionPlaybackData
    )

    # Teacher review (Sprint 19)
    from sg_spec.schemas.teacher_review import (
        TeacherAnnotationType, TeacherAnnotation,
        TeacherRecommendationType, TeacherRecommendation,
        TeacherReview
    )

    # Studio roster (Sprint 20)
    from sg_spec.schemas.studio_roster import (
        StudioRosterEventType, Student, Teacher,
        Studio, StudioRosterEvent, StudioOverview
    )

    # Curriculum progression (Sprint 22)
    from sg_spec.schemas.curriculum_progression import (
        ProgressionLevel, CurriculumPrerequisite,
        CurriculumProgressionNode, CurriculumProgressionPath,
        CurriculumProgressState, CurriculumRecommendation
    )

    # Practice queue (Sprint 23)
    from sg_spec.schemas.practice_queue import (
        PracticeQueueStatus, PracticeQueuePriority,
        ScheduledPracticeAssignment, PracticeQueue,
        PracticeQueueEventType, PracticeQueueEvent
    )

    # Outcome integration (Sprint 24)
    from sg_spec.schemas.outcome_integration import (
        AssignmentOutcomeProcessingResult
    )

    # Runtime flow (Sprint 25, 26)
    from sg_spec.schemas.runtime_flow import (
        RuntimeSessionStatus, RuntimePracticeSession,
        RuntimeSessionResult, RuntimeSessionEventType,
        RuntimeSessionEvent, RuntimeEvidenceAttachmentResult
    )

    # Runtime review (Sprint 27)
    from sg_spec.schemas.runtime_review import (
        RuntimeReviewStatus, RuntimeEvidenceSummary,
        RuntimeOutcomeSummary, RuntimeReviewReport
    )

    # Longitudinal review (Sprint 28)
    from sg_spec.schemas.longitudinal_review import (
        LongitudinalTrend, DiagnosisTrendSummary,
        OutcomeTrajectorySummary, LongitudinalProgressReview
    )

    # Pedagogical ledger (Sprint 29)
    from sg_spec.schemas.pedagogical_ledger import (
        PedagogicalEvidenceSource, PedagogicalEvidenceSeverity,
        PedagogicalEvidenceEntry, PedagogicalEvidenceLedger,
        PedagogicalEvidenceSummary
    )

    # Adaptive scheduling (Sprint 30)
    from sg_spec.schemas.adaptive_scheduling import (
        SchedulingPriorityAdjustment, SchedulingRecommendationReason,
        AdaptiveSchedulingRecommendation, AdaptiveSchedulingPlan
    )

    # Teacher scheduling mediation (Sprint 31, 32)
    from sg_spec.schemas.teacher_scheduling_mediation import (
        MediationAction, TeacherSchedulingOverride,
        TeacherSchedulingMediation, EffectiveSchedulingDecision
    )

    # Pedagogical visualization (Sprint 33)
    from sg_spec.schemas.pedagogical_visualization import (
        PedagogicalVisualizationEventType, TimelineVisualizationSeverity,
        PedagogicalTimelineEvent, DiagnosisTimelineGroup,
        PedagogicalTimelineView
    )

    # Guided practice view (Sprint 34)
    from sg_spec.schemas.guided_practice_view import (
        GuidedPracticeAssignmentView, GuidedPracticePlaybackView,
        GuidedPracticeAdaptiveView, GuidedPracticeTeacherMediationView,
        GuidedPracticeSessionView
    )

    # Pedagogical narrative (Sprint 35)
    from sg_spec.schemas.pedagogical_narrative import (
        NarrativeAudience, NarrativeSeverity,
        NarrativeSection, PedagogicalNarrative
    )

    # Session workspace (Sprint 36)
    from sg_spec.schemas.session_workspace import (
        WorkspaceAudience, WorkspacePaneType,
        WorkspacePane, WorkspaceLayout,
        SessionWorkspaceProjection
    )

    # Workspace export (Sprint 37)
    from sg_spec.schemas.workspace_export import (
        WorkspaceExportFormat, WorkspaceExportRedactionLevel,
        WorkspaceExportManifest, WorkspaceExportPackage
    )

    # Frontend state (Sprint 38)
    from sg_spec.schemas.frontend_state import (
        FrontendPaneState, WorkspaceNavigationState,
        WorkspaceFrontendState
    )

    # Frontend interaction (Sprint 39)
    from sg_spec.schemas.frontend_interaction import (
        FrontendInteractionType, FrontendInteractionEvent
    )

    # Runtime boundary (Sprint 41)
    from sg_spec.schemas.runtime_boundary import (
        RuntimeBoundaryType, RuntimeBoundaryMetadata,
        RUNTIME_BOUNDARY_VERSION, PROVENANCE_FEEDBACK, PROVENANCE_GENERATED,
        COLLAPSED_BOUNDARY_WARNING,
        create_feedback_boundary, create_regeneration_boundary,
        create_deprecated_combined_boundary
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
from .practice_dashboard import *
from .session_playback import *
from .teacher_review import *
from .studio_roster import *
from .curriculum_progression import *
from .practice_queue import *
from .outcome_integration import *
from .runtime_flow import *
from .runtime_review import *
from .longitudinal_review import *
from .pedagogical_ledger import *
from .adaptive_scheduling import *
from .teacher_scheduling_mediation import *
from .pedagogical_visualization import *
from .guided_practice_view import *
from .pedagogical_narrative import *
from .session_workspace import *
from .workspace_export import *
from .frontend_state import *
from .frontend_interaction import *
from .runtime_boundary import *
from .generation import *  # Must be last (depends on coach_schemas)

__version__ = "2.0.0"
