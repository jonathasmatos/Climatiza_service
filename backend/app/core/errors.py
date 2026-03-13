class DomainError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, hint: str | None = None, action: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.hint = hint
        self.action = action


class ValidationErrorDom(DomainError):
    def __init__(self, code: str, message: str, action: str | None = None, hint: str | None = None):
        super().__init__(code=code, message=message, status_code=400, hint=hint, action=action)


class RuleConflictError(DomainError):
    def __init__(self, code: str, message: str, action: str | None = None, hint: str | None = None):
        super().__init__(code=code, message=message, status_code=409, hint=hint, action=action)
