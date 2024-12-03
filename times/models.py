from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError

POSICOES = [
    ('PG', 'Armador'),
    ('SG', 'Ala-Armador'),
    ('SF', 'Ala'),
    ('PF', 'Ala-Pivô'),
    ('C', 'Pivô'),
]

STATUS = [
    ('Lesionado', 'Lesionado'),
    ('Indisponivel', 'Indisponível'),
    ('Ativo', 'Ativo'),
]

ROLE_CHOICES = (
    ('coach', 'Coach'),
    ('player', 'Player'),
)

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O endereço de e-mail deve ser fornecido")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractUser):
    perfil = models.CharField(max_length=10, choices=ROLE_CHOICES, default='player')
    email = models.EmailField(unique=True)
    nome_completo = models.CharField(max_length=255, null=True, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_set',
        blank=True,
        help_text="Os grupos aos quais este usuário pertence.",
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_permissions_set',
        blank=True,
        help_text="As permissões específicas para este usuário.",
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Time(models.Model):
    nome = models.CharField(max_length=100, null=True, blank=True)
    regiao = models.CharField(max_length=100, null=True, blank=True)
    treinador = models.CharField(max_length=100, null=True, blank=True)
    num_jogadores = models.IntegerField(default=0, null=True, blank=True)
    vitorias = models.IntegerField(default=0, null=True, blank=True)
    derrotas = models.IntegerField(default=0, null=True, blank=True)
    campeonatos_vencidos = models.IntegerField(default=0, null=True, blank=True)
    logo = models.ImageField(upload_to='times/logos/', null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome

class Jogador(models.Model):
    nome = models.CharField(max_length=100, null=True, blank=True)
    posicao = models.CharField(max_length=2, choices=POSICOES, null=True, blank=True)
    status = models.CharField(max_length=25, choices=STATUS, null=True, blank=True)
    altura = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    pontos = models.IntegerField(default=0, null=True, blank=True)
    rebotes = models.IntegerField(default=0, null=True, blank=True)
    assistencias = models.IntegerField(default=0, null=True, blank=True)
    turnovers = models.IntegerField(default=0, null=True, blank=True)
    roubos_bola = models.IntegerField(default=0, null=True, blank=True)
    foto = models.ImageField(upload_to='jogadores/fotos/', null=True, blank=True)
    num_jogos = models.IntegerField(default=0, null=True, blank=True)
    time = models.ForeignKey(Time, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.nome

class Arena(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)
    local = models.CharField(max_length=200, null=True, blank=True)
    capacidade = models.IntegerField(null=True, blank=True)
    time_casa = models.OneToOneField(Time, on_delete=models.SET_NULL, null=True, blank=True, related_name='arena')

    def clean(self):
        if self.capacidade and self.capacidade < 0:
            raise ValidationError("A capacidade da arena não pode ser negativa.")

    def __str__(self):
        return f"{self.nome} - {self.local}"

class Partida(models.Model):
    data = models.DateTimeField(null=False, blank=False)
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE, related_name='partidas')
    time_visitante = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='partidas_visitante')  # O time da casa é determinado pela arena associada.
    placar_time_casa = models.IntegerField(default=0, null=True, blank=True)
    placar_time_visitante = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.arena.nome} - {self.data.strftime('%d/%m/%Y')}"

class EstatisticaPartida(models.Model):
    pontos = models.IntegerField(default=0, null=True, blank=True)
    rebotes = models.IntegerField(default=0, null=True, blank=True)
    assistencias = models.IntegerField(default=0, null=True, blank=True)
    turnovers = models.IntegerField(default=0, null=True, blank=True)
    roubos_bola = models.IntegerField(default=0, null=True, blank=True)
    jogador = models.ForeignKey(Jogador, on_delete=models.CASCADE, null=True, blank=True)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.jogador.nome} - {self.partida.arena.nome}"
