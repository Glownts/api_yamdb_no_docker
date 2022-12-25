'''
Функции-представления приложения api.
'''

from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.db.models import Avg

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .mixins import ListCreateDestroyViewSet, NotPUTViewSet
from .permissions import (
    AdminOnly,
    AdminOrReadOnly,
    AuthorModeratorAdminOrReadOnly
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    GetTokenSerializer,
    SelfSerializer,
    ReviewSerializer,
    SignupSerializer,
    TitleCreateSerializer,
    TitleSerializer,
    UserSerializer
)
from .utils import mail_confirmation


class CategoryViewSet(ListCreateDestroyViewSet):
    '''
    При GET-запросе возвращает список всех экземпляров класса Category
    c функцией поиска по name. GET-запрос доступен всем пользователям.

    При POST-запросе создаст экземпляр класса Category. Правом создания
    обладает только администратор. При создании обязательны поля name и
    slug. Поле slug должно быть уникальным.

    Метод DELETE доступен только администратору. При удалении обязательно
    поле slug.
    '''

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(ListCreateDestroyViewSet):
    '''
    При GET-запросе возвращает список всех экземпляров класса Genre
    c функцией поиска по name. GET-запрос доступен всем пользователям.

    При POST-запросе создаст экземпляр класса Genre. Правом создания
    обладает только администратор. При создании обязательны поля name и
    slug. Поле slug должно быть уникальным.

    Метод DELETE доступен только администратору. При удалении обязательно
    поле slug.
    '''

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    '''
    При GET-запросе возвращает список всех экземпляров класса Title
    c фильтрацией по name, genre, category и year или вернет конретный
    экземпляр класса Title c указаным title_id. GET-запрос доступен всем
    пользователям.

    При POST-запросе создаст экземпляр класса Title. Правом создания
    обладает только администратор. При создании обязательны поля name,
    year, genre и category. Нельзя добавить произведение, которое
    еще не вышло. Валидация идет на уровне модели.

    Методы PATCH и DELETE доступны только администратору.
    '''

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('rating')
    serializer_class = TitleSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH',):
            return TitleCreateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    '''
    При GET-запросе возвращает список всех экземпляров класса Review
    относящийся к определенному экземпляру класса Title или вернет конретный
    экземпляр класса Review c указаным title_id и review_id. GET-запрос
    доступен всем пользователям.

    При POST-запросе создаст экземпляр класса Review. Правом создания
    обладают только аутентифицированные пользователи. Нельзя написать
    несколько отзывов на одно произведение. Валидация идет на уровне модели.

    Методы PATCH и DELETE доступны автору, модератору и администратору.
    '''

    serializer_class = ReviewSerializer
    permission_classes = (AuthorModeratorAdminOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    '''
    При GET-запросе возвращает список всех экземпляров класса Comment
    относящийся к определенному экземпляру класса Review и Title
    или вернет конретный экземпляр класса Comment c указаным title_id,
    review_id и comment_id. GET-запрос доступен всем пользователям.

    При POST-запросе создаст экземпляр класса Comment. Правом создания
    обладают только аутентифицированные пользователи.

    Методы PATCH и DELETE доступны автору, модератору и администратору.
    '''

    serializer_class = CommentSerializer
    permission_classes = (AuthorModeratorAdminOrReadOnly,)

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        return review.comments.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        reviews = title.reviews.all()
        review = get_object_or_404(reviews, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class UserViewSet(NotPUTViewSet):
    '''
    При GET-запросе возвращает список всех экземпляров класса User
    или вернет конретный экземпляр класса User c указаным user_id.
    GET-запрос доступен только администратору. Или GET-запрос вернет
    данные учетной записи конкретного аутентифицированного пользователя.

    При POST-запросе создаст экземпляр класса User. Правом создания
    обладает только администратор. Поля username и email должны быть
    уникальны. Валидация идет на уровне модели.

    Метод PATCH доступен аутентифицированному пользователю для своей
    учетно записи или админу для всех учетных записей.

    Метод DELETE доступен только администратору.
    '''

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    lookup_field = "username"
    pagination_class = PageNumberPagination
    search_fields = ['username', ]

    @action(
        detail=False, methods=['get', 'patch'], url_path='me',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def me(self, request):
        if request.method == 'GET':
            serializer = SelfSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'PATCH':
            serializer = SelfSerializer(
                request.user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid():
                serializer.save(role=request.user.role)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup(request):
    """Функция регистрации пользователя."""
    if request.method == 'POST':
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            if not User.objects.filter(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email']
            ).exists():
                serializer.save()
            username = serializer.data['username']
            email = serializer.data['email']
            user = get_object_or_404(User, username=username, email=email)
            mail_confirmation(request, user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    """Функция получения jwt-токена."""
    if request.method == 'POST':

        serializer = GetTokenSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data['username']
            confirmation_code = serializer.data['confirmation_code']
            user = get_object_or_404(User, username=username)
            tokens = RefreshToken.for_user(user)
            access = str(tokens.access_token)
            if default_token_generator.check_token(user, confirmation_code):
                return Response({'token': access}, status=status.HTTP_200_OK)
            return Response(
                serializer.data,
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
