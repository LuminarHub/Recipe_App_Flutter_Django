from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from followers.exceptions import AlreadyFollowingError
from followers.models import Follower
from users.serializers import CustomUserSerializer
from .serializers import FollowUserSerializer
User = get_user_model()

#
# class FindFollowersListView(ListView):
#     model = Follower
#     permi
#
#     def get_queryset(self):
#         current_user_followers = self.request.user.to_user.values('id')
#         following_others = list(
#             Follower.objects.filter(from_user=self.request.user)
#             .values_list('to_user_id', flat=True))
#         users = User.objects.filter(id__in=current_user_followers).exclude(id__in=following_others).exclude(
#             id=self.request.user.id)
#         return users

@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'user_id': {
                    'type': 'integer',
                    'description': 'ID of the user to follow'
                },
            },
            'required': ['user_id'],
        }
    },
    responses={200: None}  # Define expected responses here
)


class FollowUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = FollowUserSerializer(data=request.data)
        if serializer.is_valid():
            user_to_follow_id = serializer.validated_data.get('user_id')
            user_to_follow = get_object_or_404(User, pk=user_to_follow_id)
            try:
                Follower.objects.follow_user(user=request.user, to_user=user_to_follow)
                return Response({"status":1,"success": f"You are now following {user_to_follow.username}."}, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({"status":0,"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except AlreadyFollowingError:
                return Response({"status":0,"error": "You are already following this user."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"status":0,"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"status":0},serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListFollowersAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        followers_qs = Follower.objects.filter(to_user=user)
        followers = [follower.from_user for follower in followers_qs]
        serializer = CustomUserSerializer(followers, many=True)
        context = {
            "status": 1,
            "followers": serializer.data
        }
        return Response(context,status=status.HTTP_200_OK)

from  users.models import CustomUser

class UsersList(APIView):
    def get(self, request, *args, **kwargs):
        try:
            user = request.user
            users = CustomUser.objects.all()
            serializer = CustomUserSerializer(users, many=True)
            context = {
                "status":1,
                "users":serializer.data
            }
            return Response(context,status=status.HTTP_200_OK)
        except:
            return Response({"status":0},status=status.HTTP_200_OK)
