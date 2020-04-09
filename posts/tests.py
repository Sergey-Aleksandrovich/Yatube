from django.conf import settings
from django.test import TestCase, Client, override_settings
from time import sleep

from posts.models import User, Group, Follow, Comment


class PersonalPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_access_to_page(self):
        response = self.client.get(f'/{self.user.username}/')
        self.assertEqual(response.status_code, 200, msg='After registration, a personal user page will not be created')


class PostPublishingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

    def test_access_to_page_for_user(self):
        response = self.client.get('/new/')
        self.assertEqual(response.status_code, 200, msg='Post creation page works')

    def test_redirects_after_creating_a_post(self):
        response = self.client.post('/new/', {'text': 'Проверка добавления поста'})
        self.assertRedirects(response, '/', 302, 200, msg_prefix='After creating a post')


class RedirectingAnUnauthorizedUserTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_access_to_page(self):
        response = self.client.get('/new/')
        self.assertRedirects(response, '/auth/login/?next=/new/', 302, 200, msg_prefix='For unauthorized user')


class DisplayPostOnPagesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.text = 'Проверка добавления поста'
        self.client.post('/new/', {'text': self.text})

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_display_on_the_main_page(self):
        self.client.get('/')
        response = self.client.get('/')
        self.assertContains(response, self.text, count=1, status_code=200,
                            msg_prefix='The post is not displayed on the main page'
                            )

    def test_display_on_the_user_page(self):
        response = self.client.get(f'/{self.user.username}/')
        self.assertContains(response, self.text, count=1, status_code=200,
                            msg_prefix='The post is not displayed on the user page'
                            )

    def test_display_on_the_post_page(self):
        response = self.client.get('/testuser/1/')
        self.assertContains(response, self.text, count=1, status_code=200,
                            msg_prefix='The post is not displayed on the post page'
                            )


class PostEditingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.client.post('/new/', {'text': 'Проверка добавления поста'})
        self.text = 'Проверка редактирования поста'
        self.client.post('/testuser/1/edit/', {'text': self.text})

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_display_on_the_main_page(self):
        self.client.get('/')
        response = self.client.get('/')
        self.assertContains(response, self.text, count=1, status_code=200,
                            msg_prefix='Modified post is not displayed on the main page '
                            )

    def test_display_on_the_user_page(self):
        response = self.client.get(f'/{self.user.username}/')
        self.assertContains(response, self.text, count=1, status_code=200,
                            msg_prefix='Modified post is not displayed on the user page'
                            )

    def test_display_on_the_post_page(self):
        response = self.client.get('/testuser/1/')
        self.assertContains(response, self.text, count=1, status_code=200,
                            msg_prefix='Modified post is not displayed on the post page'
                            )


class ErrorsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_404_errors(self):
        response = self.client.get('/check/404/')
        self.assertEqual(response.status_code, 404, msg='Server does not return 404 error')


class ImagesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.group = Group.objects.create(title='Cat', slug='Cat')
        with open('posts/1.jpg', 'rb') as img:
            self.client.post('/new/', {'text': 'Добавления поста с картинкой', 'image': img, 'group': self.group.pk})

    def test_tag_img_post(self):
        response = self.client.get('/testuser/1/')
        self.assertContains(response, '<img', count=1, status_code=200, msg_prefix='')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_tag_img_index(self):
        self.client.get('/')
        response = self.client.get('/')
        self.assertContains(response, '<img', count=1, status_code=200, msg_prefix='')

    def test_tag_img_group(self):
        response = self.client.get(f'/group/{self.group.slug}')
        self.assertContains(response, '<img', count=1, status_code=200, msg_prefix='')

    def test_tag_img_profile(self):
        with open('posts/1.jpg', 'rb') as img:
            self.client.post('/new/', {'text': 'Проверка добавления поста', 'image': img})
        response = self.client.get(f'/{self.user.username}/')
        self.assertContains(response, '<img', status_code=200, msg_prefix='')

    def test_protect(self):
        with open('manage.py') as img:
            response = self.client.post('/new/', {'text': 'Проверка добавления поста', 'image': img})
        self.assertFormError(response, form='form', field='image',
                             errors='Загрузите правильное изображение. Файл, который вы загрузили, поврежден или не является изображением.',
                             msg_prefix='')


class CacheTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.client.get('/')
        self.text = 'Проверка добавления поста'
        self.client.post('/new/', {'text': self.text})

    def test_cache(self):
        response = self.client.get('/')
        self.assertNotContains(response, self.text, status_code=200, msg_prefix='')
        sleep(20)
        response = self.client.get('/')
        self.assertContains(response, self.text, count=1, status_code=200, msg_prefix='')


class SubscriptionTest(TestCase):
    def setUp(self):
        self.follower_user = User.objects.create_user(username='testuser', password='testpass')
        self.following_user = User.objects.create_user(username='testsubscription', password='testsubscription')
        self.follower = Client()
        self.follower.login(username='testuser', password='testpass')

    def test_record_in_follow(self):
        self.follower.get('/testsubscription/follow/')
        self.assertTrue(Follow.objects.filter(user=self.follower_user, author=self.following_user).exists(),
                        msg='No subscription record')
        self.follower.get('/testsubscription/unfollow/')
        self.assertFalse(Follow.objects.filter(user=self.follower_user, author=self.following_user).exists(),
                         msg='Subscription record is not deleted')


class DisplayPostOnPageFollowTest(TestCase):
    def setUp(self):
        self.follower_user = User.objects.create_user(username='testuser', password='testpass')
        self.following_user = User.objects.create_user(username='testsubscription', password='testsubscription')
        self.follower = Client()
        self.following = Client()
        self.follower.login(username='testuser', password='testpass')
        self.following.login(username='testsubscription', password='testsubscription')
        self.following.post('/new/', {'text': 'Пост'})

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_display_a_post_for_a_subscribed_user(self):
        self.follower.get('/testsubscription/follow/')
        response = self.follower.get('/follow/')
        self.assertContains(response, 'Пост', count=1, status_code=200, msg_prefix='')

    @override_settings(CACHES=settings.TEST_CACHES)
    def test_display_a_post_for_a_unsubscribed_user(self):
        self.follower.get('/testsubscription/unfollow/')
        response = self.follower.get('/follow/')
        self.assertNotContains(response, 'Пост ', status_code=200, msg_prefix='')


class PostCommentingTest(TestCase):
    def setUp(self):
        self.authorized_user = User.objects.create_user(username='testuser', password='testpass')
        self.authorized = Client()
        self.authorized.login(username='testuser', password='testpass')
        self.unauthorized = Client()
        self.text = 'Проверка добавления комментария авторизованным пользователем'
        self.authorized.post('/new/', {'text': 'Пост'})

    def test_comment_by_an_authorized_user(self):
        self.authorized.post('/testuser/1/comment/',
                             {'text': self.text})
        self.assertTrue(
            Comment.objects.filter(text=self.text).exists())
        response = self.authorized.get('/testuser/1/')
        self.assertContains(response, self.text, count=1,
                            status_code=200, msg_prefix='')

    def test_comment_by_an_unauthorized_user(self):
        self.text = 'Проверка добавления коментария неавторизованным пользователем'
        self.unauthorized.post('/testuser/1/comment/', {'text': self.text})
        self.assertFalse(
            Comment.objects.filter(text=self.text).exists())
        response = self.client.get('/testuser/1/')
        self.assertNotContains(response, self.text,
                               status_code=200, msg_prefix='')
