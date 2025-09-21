from rest_framework import viewsets, permissions, response
from .models import Event, Ticket
from .serializers import EventSerializer, TicketSerializer
from .permissions import IsAdminOrSuperUser, IsOrganizerOrReadOnly, IsOrganizerOfEvent
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from .models import Media
from .serializers import MediaSerializer
from DicoEvent.minio_client import minio_client, BUCKET_NAME
import mimetypes
from rest_framework.decorators import action


MAX_FILE_SIZE = 500 * 1024  # 500 KB
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

    @action(detail=False, methods=['post'], url_path='upload', parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        file_obj = request.FILES.get("image")
        event_id = request.data.get("event")

        if not event_id:
            return Response({"error": "'event' ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        if not file_obj:
            return Response({"error": "'image' file are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validasi ukuran file
        if file_obj.size > MAX_FILE_SIZE:
            return Response({"error": "File too large. Max 500KB allowed."}, status=status.HTTP_400_BAD_REQUEST)

        # Validasi mime type
        mime_type, _ = mimetypes.guess_type(file_obj.name)
        if not mime_type or not mime_type.startswith("image/"):
            return Response({"error": "Invalid file type. Only images allowed."}, status=status.HTTP_400_BAD_REQUEST)

        # Upload ke Minio
        minio_client.put_object(
            BUCKET_NAME,
            file_obj.name,
            file_obj.file,
            length=file_obj.size,
            content_type=mime_type,
        )

        # Simpan ke database
        media = Media.objects.create(
            image=file_obj.name,
            event_id=event_id
        )

        serializer = MediaSerializer(media)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='poster')
    def poster(self, request, pk=None):
        event = self.get_object()
        medias = event.media.all()

        if not medias.exists():
            return Response([], status=status.HTTP_200_OK)  # balikin array kosong kalau belum ada

        result = []
        for media in medias:
            try:
                url = minio_client.presigned_get_object(BUCKET_NAME, media.image)
            except Exception:
                url = None

            result.append({
                "id": str(media.id),
                "image": media.image,
                "url": url
            })

        return Response(result, status=status.HTTP_200_OK)


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
