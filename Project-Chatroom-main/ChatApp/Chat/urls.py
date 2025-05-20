from django.urls import path
from .views import (
    login_view,
    signup_view,
    logout_view,
    chat_dashboard,
    create_chat,
    chatPage,
    rename_chat,
    delete_chat
    # Accept chat request view, add when implemented
)

urlpatterns = [
    path("", login_view, name="login"),  # Root URL
    path("login/", login_view, name="login-user"),
    path("logout/", logout_view, name="logout"),
    path("signup/", signup_view, name="signup"),

    path("chat/", chat_dashboard, name="chat-page"),
    path("chat/<int:chat_id>/", chatPage, name="chat-detail"),
    path("chat/create/", create_chat, name="create-chat"),
    # path("chat/accept/<int:request_id>/", accept_chat_request, name="accept-chat"),  # Add when available
    path("chat/<int:chat_id>/rename/", rename_chat, name="rename-chat"),
    path("chat/<int:chat_id>/delete/", delete_chat, name="delete-chat"),
]
