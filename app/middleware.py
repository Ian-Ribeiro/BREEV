import threading

_thread_locals = threading.local()


def get_current_user():
    """Retorna o usuário armazenado no thread-local pelo middleware.

    Pode retornar None se a requisição não tiver usuário autenticado ou
    se o middleware não estiver ativado.
    """
    return getattr(_thread_locals, 'user', None)


class CurrentUserMiddleware:
    """Middleware simples que armazena request.user em thread-local.

    Adicione este middleware em `MIDDLEWARE` no settings.py, de preferência
    depois da autenticação (ex.: depois de 'django.contrib.auth.middleware.AuthenticationMiddleware').
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # guarda user no thread-local para que modelos/sinais possam acessá-lo
        _thread_locals.user = getattr(request, 'user', None)
        try:
            response = self.get_response(request)
            return response
        finally:
            # limpa para evitar vazamento entre requests
            try:
                del _thread_locals.user
            except Exception:
                pass
