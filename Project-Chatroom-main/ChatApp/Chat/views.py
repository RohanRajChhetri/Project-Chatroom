from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.models import User

from .forms import SignUpForm, LoginForm, ChatCreationForm, CustomUserCreationForm
from .models import Chat, Message, ChatParticipant, ChatRequest

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. Please log in.")
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'Chat/signupPage.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("chat-page")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "Chat/loginPage.html", {"form": form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login-user")

@login_required
def chat_dashboard(request):
    user = request.user

    # Get all chat IDs where user is a participant
    chat_ids = ChatParticipant.objects.filter(user=user).values_list('chat_id', flat=True)

    # Get Chat objects
    chats = Chat.objects.filter(id__in=chat_ids)

    # Attach other_user attribute for non-group chats
    for chat in chats:
        if not chat.is_group:
            # Get all participants for this chat except current user
            participants = ChatParticipant.objects.filter(chat=chat).exclude(user=user)
            chat.other_user = participants.first().user if participants.exists() else None
        else:
            chat.other_user = None  # groups have no single other_user

    # Chat requests targeting this user
    chat_requests = ChatRequest.objects.filter(to_users=user, accepted=False)

    context = {
        'chats': chats,
        'chat_requests': chat_requests,
    }
    return render(request, 'Chat/chatDashboardPage.html', context)

@login_required
def create_chat(request):
    if request.method == 'POST':
        form = ChatCreationForm(request.POST)
        if form.is_valid():
            selected_user_ids = request.POST.getlist('users')
            chat_name = request.POST.get('chat_name', '').strip()
            is_group = len(selected_user_ids) > 1

            chat = Chat.objects.create(
                name=chat_name if is_group else '',
                is_group=is_group
            )

            ChatParticipant.objects.create(chat=chat, user=request.user)

            for user_id in selected_user_ids:
                if str(user_id) != str(request.user.id):
                    ChatParticipant.objects.create(chat=chat, user_id=user_id)

            return redirect('chat-detail', chat_id=chat.id)
    else:
        form = ChatCreationForm()
        users = User.objects.exclude(id=request.user.id)
        return render(request, 'Chat/createChatPage.html', {'form': form})

@login_required
def chatPage(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    # Permission check
    if not ChatParticipant.objects.filter(chat=chat, user=request.user).exists():
        messages.error(request, "You are not a participant of this chat.")
        return redirect("chat-page")

    if request.method == "POST":
        content = request.POST.get("message", "").strip()
        if content:
            Message.objects.create(chat=chat, sender=request.user, content=content)
            return redirect("chat-detail", chat_id=chat.id)

    participants = [cp.user for cp in chat.chatparticipant_set.select_related('user').all()]
    messages_list = Message.objects.filter(chat=chat).order_by("timestamp")

    # Get the other participant in a 1-to-1 chat
    other_user = None
    if not chat.is_group:
        for participant in participants:
            if participant != request.user:
                other_user = participant
                break

    return render(request, "Chat/chatPage.html", {
        "chat": chat,
        "messages": messages_list,
        "participants": participants,
        "other_user": other_user,
    })

@require_POST
@login_required
def rename_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if not chat.is_group:
        messages.error(request, "Only group chats can be renamed.")
        return redirect("chat-detail", chat_id=chat.id)

    if not ChatParticipant.objects.filter(chat=chat, user=request.user).exists():
        messages.error(request, "You are not a participant of this chat.")
        return redirect("chat-page")

    new_name = request.POST.get("new_name", "").strip()
    if new_name:
        chat.name = new_name
        chat.save()
        messages.success(request, "Chat name updated.")
    else:
        messages.error(request, "Chat name cannot be empty.")

    return redirect("chat-detail", chat_id=chat.id)

@require_POST
@login_required
def delete_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)

    if not ChatParticipant.objects.filter(chat=chat, user=request.user).exists():
        messages.error(request, "You cannot delete this chat.")
        return redirect("chat-page")

    chat.delete()
    messages.success(request, "Chat deleted.")
    return redirect("chat-page")
