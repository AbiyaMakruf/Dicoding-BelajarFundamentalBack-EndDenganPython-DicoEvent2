from rest_framework import viewsets, permissions, response
from .models import Event, Ticket
from .serializers import EventSerializer, TicketSerializer
from .permissions import IsAdminOrSuperUser, IsOrganizerOrReadOnly, IsOrganizerOfEvent

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        if self.request.user.is_superuser or self.request.user.groups.filter(name="admin").exists():
            return [permissions.IsAuthenticated()]
        if self.request.user.groups.filter(name="organizer").exists():
            return [permissions.IsAuthenticated(), IsOrganizerOrReadOnly()]
        return [IsAdminOrSuperUser()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return response.Response({"events": serializer.data})

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOrganizerOfEvent()]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return response.Response({"tickets": serializer.data})

from .models import Registration
from .serializers import RegistrationSerializer
from .permissions import IsOwnerOrAdminOrOrganizer

class RegistrationViewSet(viewsets.ModelViewSet):
    queryset = Registration.objects.all()
    serializer_class = RegistrationSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated(), IsOwnerOrAdminOrOrganizer()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name="admin").exists():
            queryset = self.get_queryset()
        elif request.user.groups.filter(name="organizer").exists():
            queryset = Registration.objects.filter(ticket__event__organizer=request.user)
        else:
            queryset = Registration.objects.filter(user=request.user)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response({"registrations": serializer.data})

from .models import Payment
from .serializers import PaymentSerializer
from .permissions import IsOwnerOrAdminOrOrganizerPayment

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated(), IsOwnerOrAdminOrOrganizerPayment()]
        return [permissions.IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.groups.filter(name="admin").exists():
            queryset = self.get_queryset()
        elif request.user.groups.filter(name="organizer").exists():
            queryset = Payment.objects.filter(registration__ticket__event__organizer=request.user)
        else:
            queryset = Payment.objects.filter(registration__user=request.user)

        serializer = self.get_serializer(queryset, many=True)
        return response.Response({"payments": serializer.data})
