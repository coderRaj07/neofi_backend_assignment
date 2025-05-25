from deepdiff import DeepDiff
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Event, EventVersion, EventPermission
from .serializers import EventSerializer, ShareEventSerializer, EventVersionSerializer


## To be used with path('events/batch/', EventBatchCreateView.as_view(), name='event-batch-create'), # better create it as actions to prevent order issue
## This logic is shifted to actions inside EventViewSet
# class EventBatchCreateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         events_data = request.data.get('events', [])
#         serializer = EventSerializer(data=events_data, many=True, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         with transaction.atomic():
#             events = serializer.save(owner=request.user)
#             # Optionally create versions for each event here
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

    
class UpdateEventPermissionView(APIView):

    def put(self, request, event_id, user_id):  # arguments are exactly same as defined in url patterns
        event = get_object_or_404(Event, id=event_id)
        # Check if request.user is Owner
        if not event.has_role(request.user, 'Owner'):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        role = request.data.get('role')
        if role not in ['Owner', 'Editor', 'Viewer']:
            return Response({'detail': 'Invalid role.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update or create permission
        perm, created = EventPermission.objects.update_or_create(
            event=event, user_id=user_id,
            defaults={'role': role}
        )
        return Response({'detail': 'Permission updated.'})

class RemoveEventPermissionView(APIView):

    def delete(self, request, event_id, user_id):
        event = get_object_or_404(Event, id=event_id)
        if not event.has_role(request.user, 'Owner'):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        perm = EventPermission.objects.filter(event=event, user_id=user_id).first()
        if perm:
            perm.delete()
            return Response({'detail': 'Permission removed.'})
        return Response({'detail': 'Permission not found.'}, status=status.HTTP_404_NOT_FOUND)

class EventVersionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, versionId):
        event = get_object_or_404(Event, id=id)
        if not event.user_has_access(request.user):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        version = get_object_or_404(EventVersion, id=versionId, event=event)
        return Response(version.data)  # assuming version.data is JSONField or dict


class EventVersionDiffView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id, versionId1, versionId2):
        event = get_object_or_404(Event, id=id)
        if not event.user_has_access(request.user):
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        v1 = get_object_or_404(EventVersion, id=versionId1, event=event)
        v2 = get_object_or_404(EventVersion, id=versionId2, event=event)

        diff = DeepDiff(v1.data, v2.data, ignore_order=True).to_dict()
        return Response(diff)


class EventPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'

class EventViewSet(viewsets.ModelViewSet):

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['start_time', 'end_time', 'is_recurring']
    ordering_fields = ['start_time', 'end_time']

    def get_queryset(self):
        user = self.request.user
        # Filter events by user access permissions
        return Event.objects.filter(
            Q(owner=user) | Q(permissions__user=user) # look if owner is the creator itself or the event is shared with intended users
        ).distinct()

    # Create multiple events in a single request
    @action(detail=False, methods=['post'], url_path='batch', url_name='batch-create')
    def batch_create(self, request):
        events_data = request.data.get('events', [])
        serializer = EventSerializer(data=events_data, many=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            events = serializer.save(owner=request.user)
            for event in events:
                EventPermission.objects.create(event=event, user=request.user, role='owner') # add owner to every created event
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        event = serializer.save(owner=self.request.user)
        EventPermission.objects.create(event=event, user=self.request.user, role='owner')
        EventVersion.objects.create(event=event, version_number=1, **serializer.validated_data, modified_by=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.save()
        last_version = instance.versions.first()
        new_version = last_version.version_number + 1 if last_version else 1
        EventVersion.objects.create(
            event=instance,
            version_number=new_version,
            title=instance.title,
            description=instance.description,
            start_time=instance.start_time,
            end_time=instance.end_time,
            location=instance.location,
            modified_by=self.request.user
        )

    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        self.check_object_permissions(request, event)
        serializer = ShareEventSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        for user_data in serializer.validated_data['users']:
            EventPermission.objects.update_or_create(
                event=event,
                user_id=user_data['user_id'],
                defaults={'role': user_data['role']}
            )
        return Response({"status": "Permissions updated"})

    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        perms = event.permissions.values('user_id', 'role')
        return Response(perms)

    @action(detail=True, methods=['get'])
    def changelog(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        versions = EventVersion.objects.filter(event=event)
        serializer = EventVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='rollback/(?P<versionId>[^/.]+)')
    def rollback(self, request, pk=None, versionId=None):
        event = get_object_or_404(Event, pk=pk)
        version = get_object_or_404(EventVersion, event=event, version_number=versionId)
        event.title = version.title
        event.description = version.description
        event.start_time = version.start_time
        event.end_time = version.end_time
        event.location = version.location
        event.save()
        return Response({"status": "Rolled back to version {}".format(versionId)})
    
    @action(detail=True, methods=['delete'], url_path='share')
    def unshare(self, request, pk=None):
        event = get_object_or_404(Event, pk=pk)
        self.check_object_permissions(request, event)
        
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent removing the owner
        if event.owner_id == int(user_id):
            return Response({"error": "Cannot remove owner from event"}, status=status.HTTP_403_FORBIDDEN)

        try:
            permission = EventPermission.objects.get(event=event, user_id=user_id)
            permission.delete()
            return Response({"status": f"User {user_id} removed from event"}, status=status.HTTP_200_OK)
        except EventPermission.DoesNotExist:
            return Response({"error": "User does not have permission on this event"}, status=status.HTTP_404_NOT_FOUND)

