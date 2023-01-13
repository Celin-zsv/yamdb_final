from datetime import datetime

from django.db import IntegrityError
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title, User


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError('Oh! Not _me_!')
        return value


class UserSerializer(UserSignupSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        model = Review
        fields = ('id', 'author', 'text', 'score', 'pub_date')
        read_only_fields = ('pub_date', 'id',)

    def validate_score(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError(
                'Оценка должна быть в диапазоне от 1 до 10')
        return value

    def create(self, validated_data):
        review = None
        try:
            review = Review.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {'detail': 'Вы можете оставить только один отзыв.'})
        return review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('pub_date', 'id',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitlesListSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    genre = GenresSerializer(many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )

    def get_rating(self, obj):
        return obj.avg_score


class TitlesSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True, slug_field='slug', queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, value):
        current_year = datetime.now().year
        if not 0 <= value <= current_year:
            raise serializers.ValidationError(
                'Проверьте год создания произведения'
                '(не может быть больше текущего).'
            )
        return value
