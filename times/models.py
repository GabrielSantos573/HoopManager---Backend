from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from datetime import timezone

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

STATUS_PARTIDA = [
    ('Agendada', 'agendada'),
    ('Em Andamento', 'em andamento'),
    ('Finalizada', 'finalizada'),
]

STATUS_PARTIDA_LOCAL = [
    ('Em casa', 'Em casa'),
    ('Fora', 'Fora'),
]

REGIAO = [
    ('Norte', 'Norte'),
    ('Nordeste', 'Nordeste'),
    ('Centro-Oeste', 'Centro-Oeste'),
    ('Sudeste', 'Sudeste'),
    ('Sul', 'Sul'),
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
    regiao = models.CharField(max_length=100, choices=REGIAO, null=True, blank=True)
    treinador = models.CharField(max_length=100, null=True, blank=True)
    endereco = models.CharField(max_length=100, null=True, blank=True)
    num_jogadores = models.IntegerField(default=0, null=True, blank=True)
    vitorias = models.IntegerField(default=0, null=True, blank=True)
    derrotas = models.IntegerField(default=0, null=True, blank=True)
    logo = models.ImageField(upload_to='times/logos/', null=True, blank=True)
    descricao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome if self.nome else "Time sem Nome"

    def validar_numero_jogadores(self):
        if self.num_jogadores < 1:
            raise ValidationError("O time deve ter pelo menos 5 jogadores.")

    def clean(self):
        if self.nome and (len(self.nome) < 3 or len(self.nome) > 25):
            raise ValidationError("O nome do time deve ter entre 3 e 25 caracteres.")
        if self.treinador and (len(self.treinador) < 3 or len(self.treinador) > 25):
            raise ValidationError("O nome do treinador deve ter entre 3 e 25 caracteres.")
        if self.num_jogadores < 2:
            raise ValidationError("O time deve ter pelo menos 5 jogadores.")
        if self.vitorias < 0 or self.derrotas < 0:
            raise ValidationError("Vitórias e derrotas não podem ser negativas.")
        self.validar_numero_jogadores

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Jogador(models.Model):
    nome = models.CharField(max_length=100, null=True, blank=True)
    posicao = models.CharField(max_length=2, choices=POSICOES, null=True, blank=True)
    idade = models.IntegerField(default=0, null=True, blank=True)
    status = models.CharField(max_length=25, choices=STATUS, null=True, blank=True)
    altura = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    peso = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
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

    def clean(self):
        if self.nome and len(self.nome) < 3:
            raise ValidationError("O nome do jogador deve ter pelo menos 3 caracteres.")
        if self.idade <= 12:
            raise ValidationError("A idade deve ser maior que 12 anos.")
        if self.altura and self.altura <= 0:
            raise ValidationError("A altura deve ser positiva.")
        if self.peso and self.peso <= 0:
            raise ValidationError("O peso deve ser positivo.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Arena(models.Model):
    nome = models.CharField(max_length=100, null=False, blank=False)
    local = models.CharField(max_length=200, null=True, blank=True)
    capacidade = models.IntegerField(null=True, blank=True)
    time = models.OneToOneField(Time, on_delete=models.CASCADE, null=True, blank=True, related_name='arena')
    
    def __str__(self):
        return f"{self.nome} - {self.local}"

    def clean(self):
        if self.capacidade is not None and self.capacidade < 0:
            raise ValidationError("A capacidade da arena não pode ser negativa.")
        if self.nome and len(self.nome) < 3:
            raise ValidationError("O nome da arena deve ter pelo menos 3 caracteres.")
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class Partida(models.Model):
    data = models.DateTimeField(null=False, blank=False)
    arena = models.ForeignKey(Arena, on_delete=models.CASCADE, related_name='partidas', null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS_PARTIDA, null=True, blank=True)
    status_local = models.CharField(max_length=15, choices=STATUS_PARTIDA_LOCAL, null=True, blank=True)
    time = models.ForeignKey(Time, on_delete=models.CASCADE, null=True,related_name='partidas_como_time')  # Time principal
    time_adversario = models.CharField(max_length=100, null=True, blank=True)  # Apenas o nome do time adversário
    placar_time_casa = models.IntegerField(default=0, null=True, blank=True)
    placar_time_visitante = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.time.nome} vs {self.time_adversario} - {self.data.strftime('%d/%m/%Y %H:%M')}"

    def clean(self):
        if self.placar_time_casa < 0 or self.placar_time_visitante < 0:
            raise ValidationError("Os placares não podem ser negativos.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class EstatisticaPartida(models.Model):
    pontos = models.IntegerField(default=0, null=True, blank=True)
    rebotes = models.IntegerField(default=0, null=True, blank=True)
    assistencias = models.IntegerField(default=0, null=True, blank=True)
    turnovers = models.IntegerField(default=0, null=True, blank=True)
    roubos_bola = models.IntegerField(default=0, null=True, blank=True)
    jogador = models.ForeignKey(Jogador, on_delete=models.CASCADE, null=True, blank=True)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, null=True, blank=True)
    #tempo_jogo = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)

    def clean(self):
        if self.pontos < 0 or self.rebotes < 0 or self.assistencias < 0 or self.turnovers < 0 or self.roubos_bola < 0:
            raise ValidationError("Estatísticas não podem conter valores negativos.")

    def __str__(self):
        return f"{self.jogador.nome} - {self.partida.arena.nome}"
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

