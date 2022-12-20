'''
Функции-представления приложения api.

Не хватает представления модели User
'''

from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from reviews.models import Category, Genre, Title, User
from rest_framework import viewsets, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.viewsets import GenericViewSet, ModelViewSet, mixins
from .permissions import (
    AdminOrReadOnly,
    AuthorOrReadOnly,
    MeOrAdminOnly
)
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer,
    UserSerializer,
    RegisterSerializer,
    TokenSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
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

    def perform_create(self, serializer):
        return serializer.save()


class GenreViewSet(viewsets.ModelViewSet):
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

    def perform_create(self, serializer):
        return serializer.save()


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

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'genre__slug', 'category__slug', 'year',)

    def perform_create(self, serializer):
        return serializer.save()


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
    permission_classes = (AuthorOrReadOnly,)

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
    permission_classes = (AuthorOrReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        reviews = title.reviews.all()
        review = get_object_or_404(reviews, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        reviews = title.reviews.all()
        review = get_object_or_404(reviews, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = get_object_or_404(
        User,
        username=serializer.validated_data["username"]
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject="regisrted in Yambd",
        message=f"confirmation code: {confirmation_code}",
        from_email=None,
        recipient_list=[user.email],
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_jwt_token(request):
    serializer = TokenSerializer(data=request.data)
    if serializer.is_valid():
        user = get_object_or_404(
            User,
            username=request.data.get('username')
        )
        c_code = user.confirmation_code
        if request.data['confirmation_code'] == c_code:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
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

    serializer_class = UserSerializer
    permission_classes = (MeOrAdminOnly, )
    lookup_field = "Username"
    queryset = User.objects.all()
    pagination_class = PageNumberPagination
    @action(
        methods=[
            "GET",
            "PATCH",
        ],
        detail=False,
        url_path="me",
        permission_classes=[permissions.IsAuthenticated],
    )
    def users_own_profile(self, request):
        user = request.user
        if request.method == "GET":
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == "PATCH":
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


