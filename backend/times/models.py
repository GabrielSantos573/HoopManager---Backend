from django.db import models

# Create your models here.

POSICOES = [
    ('PG', 'Armador'),
    ('SG', 'Ala-Armador'),
    ('SF', 'Ala'),
    ('PF', 'Ala-Pivô'),
    ('C', 'Pivô'),
]

class Time(models.Model):
    nome = models.CharField(max_length=100, null=True, blank=True)
    regiao = models.CharField(max_length=100, null=True, blank=True)
    treinador = models.CharField(max_length=100, null=True, blank=True)
    num_jogadores = models.IntegerField(default=0, null=True, blank=True)
    vitorias = models.IntegerField(default=0, null=True, blank=True)
    derrotas = models.IntegerField(default=0, null=True, blank=True)
    campeonatos_vencidos = models.IntegerField(default=0, null=True, blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)  # Para armazenar imagens de logo
    descricao = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nome

class Jogador(models.Model):
    nome = models.CharField(max_length=100, null=True, blank=True)
    posicao = models.CharField(max_length=2, choices=POSICOES, null=True, blank=True)
    altura = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    pontos = models.IntegerField(default=0, null=True, blank=True)
    rebotes = models.IntegerField(default=0, null=True, blank=True)
    assistencias = models.IntegerField(default=0, null=True, blank=True)
    turnovers = models.IntegerField(default=0, null=True, blank=True)
    roubos_bola = models.IntegerField(default=0, null=True, blank=True)
    num_jogos = models.IntegerField(default=0, null=True, blank=True)
    time = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='jogadores')
    def __str__(self):
        return self.nome

