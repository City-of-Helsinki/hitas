from hitas.exceptions import GenericNotFound, InternalServerError


def handle_404(request, exception=None) -> GenericNotFound:  # NOSONAR
    return GenericNotFound()


def handle_500(request) -> InternalServerError:  # NOSONAR
    return InternalServerError()
