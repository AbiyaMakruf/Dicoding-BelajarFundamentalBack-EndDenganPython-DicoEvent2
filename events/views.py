import mimetypes
from django.core.cache import cache
from rest_framework import viewsets, permissions, status, response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Event, Ticket, Media, Registration, Payment
from .serializers import (
    EventSerializer,
    TicketSerializer,
    MediaSerializer,
    RegistrationSerializer,
    PaymentSerializer,
)
from .permissions import (
    IsAdminOrSuperUser,
    IsOrganizerOrReadOnly,
    IsOrganizerOfEvent,
    IsOwnerOrAdminOrOrganizer,
    IsOwnerOrAdminOrOrganizerPayment,
)
from DicoEvent.minio_client import minio_client, BUCKET_NAME

MAX_FILE_SIZE = 500 * 1024  # 500 KB


# =========================================================
# EVENT VIEWSET
# =========================================================
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
        return Response({"events": serializer.data})

    # 🔹 Detail dengan cache Redis
    def retrieve(self, request, *args, **kwargs):
        event_id = kwargs.get("pk")
        cache_key = f"event:{event_id}"

        data = cache.get(cache_key)
        if data:
            resp = Response(data)
            resp["X-Data-Source"] = "cache"
            return resp

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        cache.set(cache_key, data, timeout=3600)
        return Response(data)

    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete(f"event:{instance.id}")
        return instance

    def perform_destroy(self, instance):
        cache.delete(f"event:{instance.id}")
        return super().perform_destroy(instance)

    # 🔹 Upload poster
    @action(
        detail=False,
        methods=["post"],
        url_path="upload",
        parser_classes=[MultiPartParser, FormParser],
    )
    def upload(self, request):
        file_obj = request.FILES.get("image")
        event_id = request.data.get("event")

        if not event_id:
            return Response({"error": "'event' ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not file_obj:
            return Response({"error": "'image' file is required."}, status=status.HTTP_400_BAD_REQUEST)

        if file_obj.size > MAX_FILE_SIZE:
            return Response({"error": "File too large. Max 500KB allowed."}, status=status.HTTP_400_BAD_REQUEST)

        mime_type, _ = mimetypes.guess_type(file_obj.name)
        if not mime_type or not mime_type.startswith("image/"):
            return Response({"error": "Invalid file type. Only images allowed."}, status=status.HTTP_400_BAD_REQUEST)

        minio_client.put_object(
            BUCKET_NAME,
            file_obj.name,
            file_obj.file,
            length=file_obj.size,
            content_type=mime_type,
        )

        media = Media.objects.create(image=file_obj.name, event_id=event_id)
        serializer = MediaSerializer(media)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # 🔹 Ambil semua poster event
    @action(detail=True, methods=["get"], url_path="poster")
    def poster(self, request, pk=None):
        event = self.get_object()
        medias = event.media.all()

        if not medias.exists():
            return Response([], status=status.HTTP_200_OK)

        result = []
        for media in medias:
            try:
                url = minio_client.presigned_get_object(BUCKET_NAME, media.image)
            except Exception:
                url = None

            result.append(
                {
                    "id": str(media.id),
                    "image": media.image,
                    "url": url,
                }
            )

        return Response(result, status=status.HTTP_200_OK)


# =========================================================
# TICKET VIEWSET
# =========================================================
class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOrganizerOfEvent()]

    # 🔹 List dengan cache
    def list(self, request, *args, **kwargs):
        cache_key = "tickets:list"
        data = cache.get(cache_key)

        if data:
            resp = Response(data)
            resp["X-Data-Source"] = "cache"
            return resp

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = {"tickets": serializer.data}

        cache.set(cache_key, data, timeout=3600)
        return Response(data)

    # 🔹 [TAMBAHKAN INI] Detail dengan cache Redis
    def retrieve(self, request, *args, **kwargs):
        ticket_id = kwargs.get("pk")
        cache_key = f"ticket:{ticket_id}"

        data = cache.get(cache_key)
        if data:
            resp = Response(data)
            resp["X-Data-Source"] = "cache"
            return resp

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data

        cache.set(cache_key, data, timeout=3600)
        return Response(data)

    def perform_create(self, serializer):
        cache.delete("tickets:list")  # Hapus cache untuk list
        return serializer.save()

    # 🔹 [UPDATE INI] Hapus cache list dan detail
    def perform_update(self, serializer):
        instance = serializer.save()
        cache.delete("tickets:list")  # Hapus cache untuk list
        cache.delete(f"ticket:{instance.id}")  # Hapus cache untuk detail tiket ini
        return instance

    # 🔹 [UPDATE INI] Hapus cache list dan detail
    def perform_destroy(self, instance):
        cache.delete("tickets:list")  # Hapus cache untuk list
        cache.delete(f"ticket:{instance.id}")  # Hapus cache untuk detail tiket ini
        return super().perform_destroy(instance)



# =========================================================
# REGISTRATION VIEWSET
# =========================================================
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
        return Response({"registrations": serializer.data})


# =========================================================
# PAYMENT VIEWSET
# =========================================================
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
        return Response({"payments": serializer.data})
