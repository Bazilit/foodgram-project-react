from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Модель кастомного пользователя"""

    AUTHENTICATED = 'user'
    ADMINISTRATOR = 'admin'
    ROLE_CHOICES = [
        (AUTHENTICATED, 'Аутентифицированный пользователь'),
        (ADMINISTRATOR, 'Администратор'),
    ]
    username = models.CharField(verbose_name='Логин', unique=True,max_length=150)
    email = models.EmailField(verbose_name="Email", unique=True, db_index=True)
    first_name = models.CharField(verbose_name="Имя", max_length=150)
    last_name = models.CharField(verbose_name="Фамилия", max_length=150)
    password = models.CharField(verbose_name='Пароль', max_length=150)
    role = models.CharField(verbose_name='Роль', max_length=200,
                            choices=ROLE_CHOICES, default=AUTHENTICATED)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'password']

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('username', 'email'), name='unique_username_email'
            )
        ]
        
    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == User.ADMINISTRATOR
        
        
class Subscription(models.Model):
    """
    user — тот, кто подписывается.
    author — тот, на кого подписываются.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="subscriber", verbose_name='Подписчик')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following", verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            )
        ]        

