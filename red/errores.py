class ErrorCripta(Exception):
    pass


class ErrorRed(ErrorCripta):
    pass


class PresupuestoAgotado(ErrorCripta):
    pass


class DatosInvalidos(ErrorCripta):
    pass


class DatosNoDisponibles(ErrorCripta):
    pass


class VersionIncompatible(ErrorCripta):
    pass
