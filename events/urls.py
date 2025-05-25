from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EventViewSet,
    # EventBatchCreateView,
    UpdateEventPermissionView,
    RemoveEventPermissionView,
    EventVersionDetailView,
    EventVersionDiffView
)

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    # path('events/batch/', EventBatchCreateView.as_view(), name='event-batch-create'), # better create it as actions to prevent order issue
    path('', include(router.urls)),
    # Event Permission Management
    path('events/<uuid:event_id>/permissions/<uuid:user_id>/update/', UpdateEventPermissionView.as_view(), name='update_event_permission'),
    path('events/<uuid:event_id>/permissions/<uuid:user_id>/remove/', RemoveEventPermissionView.as_view(), name='remove_event_permission'),

    # Event Version Detail & Diff
    path('events/<uuid:event_id>/versions/<uuid:version_id>/', EventVersionDetailView.as_view(), name='event_version_detail'),
    path('events/<uuid:event_id>/versions/diff/<uuid:version_id_1>/<uuid:version_id_2>/', EventVersionDiffView.as_view(), name='event_version_diff'),
]