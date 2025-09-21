from rest_framework import serializers
from .models import Event, Ticket, Registration, Payment

class EventSerializer(serializers.ModelSerializer):
    organizer_id = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = Event
        fields = [
            'id', 'name', 'description', 'location',
            'start_time', 'end_time', 'status', 'category',
            'quota', 'organizer', 'organizer_id'
        ]
        extra_kwargs = {
            'organizer': {'read_only': True}
        }

    def create(self, validated_data):
        organizer_id = validated_data.pop('organizer_id')
        event = Event.objects.create(organizer_id=organizer_id, **validated_data)
        return event


class TicketSerializer(serializers.ModelSerializer):
    event_id = serializers.UUIDField(write_only=True, required=True)
    price = serializers.FloatField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'name', 'price', 'sales_start', 'sales_end',
            'quota', 'event', 'event_id'
        ]
        extra_kwargs = {
            'event': {'read_only': True}
        }

    def create(self, validated_data):
        event_id = validated_data.pop('event_id')
        ticket = Ticket.objects.create(event_id=event_id, **validated_data)
        return ticket

class RegistrationSerializer(serializers.ModelSerializer):
    ticket_id = serializers.UUIDField(write_only=True, required=True)
    user_id = serializers.UUIDField(write_only=True, required=True)

    class Meta:
        model = Registration
        fields = ['id', 'user', 'ticket', 'ticket_id', 'user_id', 'registered_at']
        extra_kwargs = {
            'user': {'read_only': True},
            'ticket': {'read_only': True}
        }

    def create(self, validated_data):
        ticket_id = validated_data.pop('ticket_id')
        user_id = validated_data.pop('user_id')
        registration = Registration.objects.create(user_id=user_id, ticket_id=ticket_id, **validated_data)
        return registration

class PaymentSerializer(serializers.ModelSerializer):
    registration_id = serializers.UUIDField(write_only=True, required=True)
    amount_paid = serializers.FloatField()  # agar response JSON number, bukan string

    class Meta:
        model = Payment
        fields = [
            'id', 'registration', 'registration_id',
            'payment_method', 'payment_status', 'amount_paid', 'paid_at'
        ]
        extra_kwargs = {
            'registration': {'read_only': True}
        }

    def create(self, validated_data):
        registration_id = validated_data.pop('registration_id')
        payment = Payment.objects.create(registration_id=registration_id, **validated_data)
        return payment
