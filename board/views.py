from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect
from django.db.models import Q
from accounts.models import User
from .models import Board
from .forms import BoardForm
from django.core.paginator import Paginator


def board_list(request):
    all_boards = Board.objects.all().order_by('-id')
    page = int(request.GET.get('p', 1))
    pagenator = Paginator(all_boards, 2)
    boards = pagenator.get_page(page)
    username = None
    if request.session.get('user'):
        user_id = request.session.get('user')
        username = User.objects.get(pk=user_id)
    return render(request, 'board/board_list.html', {"boards":boards, 'username': username})

@login_required
def board_write(request):
    if request.method == "POST":
        form = BoardForm(request.POST, request.FILES)

        if form.is_valid():
            # form의 모든 validators 호출 유효성 검증 수행
            user_id = request.user.id
            member = User.objects.get(pk=user_id)

            board = Board()
            board.title = form.cleaned_data['title']
            board.contents = form.cleaned_data['contents']
            board.image = form.cleaned_data['image']
            board.writer = member
            board.save()

            return redirect('/board/list/')

    else:
        form = BoardForm()

    return render(request, 'board/board_write.html', {'form': form, 'username': request.session.get('user')})

def board_detail(request, pk):
    try:
        board = Board.objects.get(pk=pk)
    except Board.DoesNotExist:
        raise Http404('게시글을 찾을 수 없습니다.')

    username = None
    if request.session.get('user'):
        user_id = request.session.get('user')
        username = User.objects.get(pk=user_id)

    is_owner = False
    if board.writer == username:
        is_owner = True

    return render(request, 'board/board_detail.html', {'board':board, 'is_owner':is_owner})

def board_modify(request, pk):
    try:
        board = Board.objects.get(pk=pk)
    except Board.DoesNotExist:
        raise Http404('게시글을 찾을 수 없습니다.')

    if request.method == "POST":
        form = BoardForm(request.POST)

        if form.is_valid():
            board.title = form.cleaned_data['title']
            board.contents = form.cleaned_data['contents']
            board.save()
            return redirect('/board/detail/' + str(board.id))

    else:
        form = BoardForm(initial={'title': board.title, 'contents': board.contents})
        context = {'form': form, 'board': board}
    return render(request, 'board/board_write.html', context)

def board_delete(request, pk):
    #if not request.session.get('user'):
    #    return redirect('/accounts/login/')
    try:
        board = Board.objects.get(pk=pk)
    except Board.DoesNotExist:
        raise Http404('게시글을 찾을 수 없습니다.')

    #if board.writer.user_id != request.session.get('user'):
    #    return redirect('/board/detail/'+str(pk))

    board.delete()
    return redirect('/board/list/')

def search_view(request):
    keyword = request.GET.get('keyword')

    results = None
    if keyword and len(keyword) >= 2:
        results = Board.objects.filter(
            Q(title__icontains=keyword) | Q(contents__icontains=keyword)
        )

    context = {
        'results': results,
        'keyword': keyword
    }

    return render(request, 'board/search.html', context)