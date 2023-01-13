from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, mixins, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import (PageNumberPagination,
                                       LimitOffsetPagination)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.filters import TitleFilter
from api.permissions import (IsAuthorAdminModeratorOrReadOnly,
                             IsAdminOrReadOnly, IsAdminOnly)
from api.serializers import (CategorySerializer, CommentSerializer,
                             GenresSerializer, ReviewSerializer,
                             TitlesSerializer, TitlesListSerializer,
                             UserSerializer, UserSignupSerializer)
from api_yamdb import settings
from reviews.models import Category, Genre, Review, Title, User


class SendConfirmationCode(mixins.CreateModelMixin,
                           viewsets.GenericViewSet
                           ):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer

    def send_confirmation_code_email(self, user):
        send_mail(
            subject='Confirmation code',
            message=default_token_generator.make_token(user),
            recipient_list=[user.email],
            from_email=settings.FROM_EMAIL,
        )

    def create(self, request):
        serializer = UserSignupSerializer(data=request.data)
        email = serializer.initial_data.get('email')
        if serializer.is_valid():
            serializer.save()
            self.send_confirmation_code_email(
                get_object_or_404(User, email=email)
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        elif User.objects.filter(
                email=email,
                username=serializer.data.get('username')).exists():
            self.send_confirmation_code_email(
                get_object_or_404(User, email=email)
            )
            return Response(
                'Confirmation code sent',
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def get_token(request):
    for attr in ['username', 'confirmation_code']:
        if attr not in request.data:
            return Response(
                {attr: 'Required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    user = get_object_or_404(User, username=request.data['username'])
    if default_token_generator.check_token(
            user, request.data['confirmation_code']):
        return Response(
            {'token': str(RefreshToken.for_user(user).access_token)}
        )
    else:
        return Response(
            {'confirmation_code': 'Error'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)

    def get_queryset(self):
        title = self.kwargs.get('title_id')
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorAdminModeratorOrReadOnly,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs['review_id'])
        serializer.save(author=self.request.user, review=review)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^username',)
    lookup_field = 'username'
    permission_classes = (IsAdminOnly, )
    pagination_class = LimitOffsetPagination

    @action(
        methods=['get', 'patch'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(self.request.user)
            return Response(serializer.data)
        if request.method == 'PATCH':
            user = get_object_or_404(User, username=self.request.user)
            serializer = UserSerializer(
                user, data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save(role=user.role)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


class CreateRetrieveDestroyViewSet(mixins.CreateModelMixin,
                                   mixins.ListModelMixin,
                                   mixins.DestroyModelMixin,
                                   viewsets.GenericViewSet):
    """
    Вьюсет, который позволяет создать или удалить объект, посмотреть список.
    Чтобы использовать его: наследуйтесь от этого класса,
    задайте атрибуты queryset и serializer_class.
    """
    pass


class CategoryViewSet(CreateRetrieveDestroyViewSet):
    """
    Вьюсет позволяет обрабатывать POST, DELETE и GET(list) запросы
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class GenresViewSet(CreateRetrieveDestroyViewSet):
    """
    Вьюсет позволяет обрабатывать POST, DELETE и GET(list) запросы
    """
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'


class TitlesViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        avg_score=Avg('reviews__score')).order_by('id')
    permission_classes = [IsAdminOrReadOnly, ]
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return TitlesSerializer
        return TitlesListSerializer
