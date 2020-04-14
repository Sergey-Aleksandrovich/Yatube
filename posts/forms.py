from django.forms import ModelForm

from posts.models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст',
                  'group': 'Группа',
                  'image': 'Изображение', }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
