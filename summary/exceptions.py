"""Domain exceptions for the distillation pipeline."""


class ValidationError(ValueError):
    """Raised when user input fails validation."""


class ExtractionError(RuntimeError):
    """Raised when source extraction fails."""


class DistillationError(RuntimeError):
    """Raised when LLM distillation fails."""


class VisualizationError(RuntimeError):
    """Raised when infographic generation fails."""
