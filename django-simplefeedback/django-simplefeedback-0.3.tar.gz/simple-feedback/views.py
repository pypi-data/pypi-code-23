from rest_framework.generics import CreateAPIView
from .serializers import TicketSerializer


class TicketCreateAPIView(CreateAPIView):
    serializer_class = TicketSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated():
            serializer.validated_data['user'] = self.request.user
        super(TicketCreateAPIView, self).perform_create(serializer)
