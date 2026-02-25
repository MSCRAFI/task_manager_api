from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer

class TaskListCreateView(generics.ListCreateAPIView):
    """
        GET /api/tasks/    - List all tasks for authenticated user
        POST /api/tasks/   - Create new task

        query params for filtering:
            ?status=pending or in_progress or completed
            ?priority=low or medium or high
            ?search=<keyword>   (title and descripiton)
            ?ordering=due_date  (or -due_date for descending)

    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'title',
        'description'
    ]
    ordering_fields = [
        'created_at',
        'due_date',
        'priority',
        'status'
    ]
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Task.objects.filter(user=self.request.user)

        # filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # filter by priority
        priority_param = self.request.query_params.get('priority')
        if priority_param:
            queryset = queryset.filter(priority=priority_param)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TaskCreateSerializer
        return TaskSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        #  returning full task details using TaskSerializer
        response_serializer = TaskCreateSerializer(task)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class TaskRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/tasks/<id>/   - get a single task
    PUT    /api/tasks/<id>/   - full update
    PATCH  /api/tasks/<id>/   - partial update
    DELETE /api/tasks/<id>/   - delete a task
    """
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        # users can only access their own tasks
        return Task.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        task = self.get_object()
        task_title = task.title
        task.delete()

        return Response(
            {'message': f'Task "{task_title}" deleted successfully.'},
            status=status.HTTP_200_OK
        )
