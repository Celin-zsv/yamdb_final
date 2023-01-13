from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api import views

app_name = 'api'

router = DefaultRouter()
router.register('auth/signup',
                views.SendConfirmationCode, basename='signup')
router.register('users', views.UserViewSet)
router.register('categories', views.CategoryViewSet)
router.register('genres', views.GenresViewSet)
router.register('titles', views.TitlesViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet, basename='reviews')
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet, basename='comments')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/token/', views.get_token),
]
