from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from .models import Room, Topic, Message
from .forms import RoomForm, MessageForm


# Create your views here.

# rooms = [ 
#     {'id':1, 'name': 'Lets learn python!'},
#     {'id':2, 'name': 'Design with me!'},
#     {'id':3, 'name': 'Frontend Developers'},   
# ]

def loginPage(request):
    page ='login'

    # Prevent a user who's already logged in and authenticated from re-logging in 
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == "POST":
        # Get username and password
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        # Check is user exists 
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        # Get user object based on username and password
        user = authenticate(request, username=username, password=password)

        # Log user in and create session in database and browser
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR Password does not exist')
    
    context = {'page':page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerPage(request):
    # page = 'register'
    form = UserCreationForm
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            # login the user that's just been registered and send them to the homepage
            login(request, user)
            return redirect('home')
        
        else:
            messages.error(request, 'An error occured during registration')

    return render(request, 'base/login_register.html', {'form': form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    # topic__name__icontains=q ; whatever value is in the topic name contains the value q, 
    # the i before contains makes it case insensitive
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )

    topics = Topic.objects.all()
    room_count = rooms.count()

    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    # Query child objects of each room 
    # set_all = many to one relationship
    room_messages = room.message_set.all().order_by('-created')
    # all = many to many relationship
    participants = room.participants.all()

    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            # In the input in room.html, we named it body
            body = request.POST.get('body')
        )
        # add a user to be a participants once they post a message / comment
        room.participants.add(request.user)
        return redirect('room', pk=room.id)


    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    # the form will be prefilled with the room value
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url='login')
def updateMessage(request, pk):
    message = Message.objects.get(id=pk)
    # the form will be prefilled with the message body
    form = MessageForm(instance=message)

    if request.user != message.user:
        return HttpResponse('You are not allowed to edit this message!')

    if request.method == 'POST':
        form = MessageForm(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/message_form.html', context)



@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed to delete this message!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})