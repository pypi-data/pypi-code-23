import threading


class AutomatedLoggingMiddleware:
  thread_local = threading.local()

  def process_request(self, request):
    request_uri = request.get_full_path()
    AutomatedLoggingMiddleware.thread_local.current_user = request.user
    AutomatedLoggingMiddleware.thread_local.request_uri = request_uri
    AutomatedLoggingMiddleware.thread_local.application = request_uri.split('/')[1]
