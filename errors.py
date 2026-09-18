"""Public errors contain fixed messages only, never provider output or input data."""


class ServiceError(Exception):
    status_code = 500
    code = "internal_error"
    message = "The request could not be completed safely."


class NotReadyError(ServiceError):
    code = "service_not_ready"
    message = "The model credentials and solver must be configured before use."


class InterpretationError(ServiceError):
    code = "invalid_interpretation"
    message = "The model did not return a valid interpretation."


class ProviderError(ServiceError):
    code = "model_unavailable"
    message = "The language model is unavailable. Please retry later."


class DeadlineError(ServiceError):
    code = "request_timeout"
    message = "The request exceeded the processing deadline."


class InfeasibleError(ServiceError):
    status_code = 422
    code = "infeasible_constraints"
    message = "No schedule satisfies all validated operating constraints."


class SolverError(ServiceError):
    code = "solver_failure"
    message = "The optimizer could not establish an optimal schedule."


class ScheduleError(ServiceError):
    code = "schedule_verification_failed"
    message = "The computed schedule failed independent verification."
