from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.paginator import Paginator

from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow


def index(request):
    post_list = Post.objects.select_related('author', 'group').order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)  # показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)  # получить записи с нужным смещением
    return render(request, 'index.html', {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related('author', 'group').filter(group=group).order_by('-pub_date').all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'page': page, 'paginator': paginator})


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.select_related('author').filter(author=author).order_by('-pub_date').all()
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=author).exists()
    else:
        following = True
    return render(request, 'profile.html',
                  {'page': page, 'author': author, 'paginator': paginator, 'following': following})


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post.objects.select_related('author'), id=post_id)
    comments = post.post_comment.all()
    form = CommentForm()
    return render(request, 'post.html', {'post': post, 'author': author, 'comments': comments, 'form': form})


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    if request.user != author:
        return redirect(f'/{username}/{post_id}')
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect(f'/{username}/{post_id}')
    return render(request, 'new_post.html', {'form': form, 'post': post})


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    comments = post.post_comment.all()
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.author = request.user
            form.post = post
            form.save()
            return redirect(f'/{username}/{post_id}')
        return render(request, 'comments.html', {'form': form, 'post': post, 'comments': comments})
    form = CommentForm()
    return render(request, 'comments.html', {'form': form, 'post': post, 'comments': comments})


@login_required
def follow_index(request):
    follows = Follow.objects.filter(user=request.user)
    author = []
    for follow in follows:
        author.append(follow.author)
    post_list = Post.objects.filter(author__in=author).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page, 'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = (Follow.objects.filter(user=request.user, author=author).exists()) or (
                request.user == author)  # Если уже подписан или пытаешься сам на себя подписаться, то редиректнет.
    if follow == True:
        return redirect(f'/{username}/')
    else:
        follow = Follow.objects.create(user=request.user, author=author)
        follow.save()
        return redirect(f'/{username}/')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author).exists()
    if follow == True:
        follow = Follow.objects.get(user=request.user, author=author)
        follow.delete()
        return redirect(f'/{username}/')
    else:
        return redirect(f'/{username}/')


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
