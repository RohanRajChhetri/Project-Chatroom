from django.contrib import admin
from .models import Message, Chat, ChatParticipant, ChatRequest

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'chat', 'timestamp', 'content')
    list_filter = ('chat', 'sender', 'timestamp')
    search_fields = ('content', 'sender__username', 'chat__name')

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_group', 'created_at')
    list_filter = ('is_group',)
    search_fields = ('name',)

@admin.register(ChatParticipant)
class ChatParticipantAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'chat', 'joined_at')
    list_filter = ('joined_at',)
    search_fields = ('user__username', 'chat__name')

@admin.register(ChatRequest)
class ChatRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'is_group', 'chat_name', 'accepted', 'created_at')
    list_filter = ('is_group', 'accepted')
    search_fields = ('from_user__username', 'chat_name')




# Register your models here.
