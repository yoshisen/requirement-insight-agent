"""Provider-related error hierarchy."""


class ProviderError(RuntimeError):
    """Base error for provider stack failures."""


class ProviderConfigurationError(ProviderError):
    """Raised when provider selection or configuration is invalid."""


class ProviderAuthenticationError(ProviderError):
    """Raised when a provider requires credentials that are missing or rejected."""


class ProviderRequestError(ProviderError):
    """Raised when an external provider call fails in transport or HTTP response."""


class ProviderNotImplementedError(ProviderError):
    """Raised for providers that are wired in but not fully implemented yet."""