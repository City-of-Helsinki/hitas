from hitas.exceptions import GenericNotFound, InternalServerError


def handle_404(request, exception=None) -> GenericNotFound:
    return GenericNotFound()


def handle_500(request) -> InternalServerError:
    return InternalServerError()
