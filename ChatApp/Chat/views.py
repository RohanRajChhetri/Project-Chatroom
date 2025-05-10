from django.shortcuts import render, redirect

from django.contrib.auth.models import User

def chatPage(request):
    users = User.objects.exclude(username=request.user.username)
    chat_with = request.GET.get('chatWith', users.first().username if users else "")
    return render(request, 'chat/chatPage.html', {
        'users': users,
        'chat_with': chat_with
    })
