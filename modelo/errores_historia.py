"""Errores esperados del dominio; sin depender de vista, red o persistencia."""


class ErrorHistoria(ValueError):
    """Base capturable al integrar comandos, compatible con ValueError."""


class EntradaHistoriaInvalida(ErrorHistoria):
    """Parámetro, tipo o formato de registro no admitido."""


class ReferenciaHistoricaInvalida(ErrorHistoria):
    """Instante o acción que no existe en la rama vigente."""


class CambioHistoriaIncoherente(ErrorHistoria):
    """Los registros no corresponden al estado o al orden temporal esperado."""
