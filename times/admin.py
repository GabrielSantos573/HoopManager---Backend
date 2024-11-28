from django.contrib import admin
from .models import Time, Jogador, Partida, EstatisticaPartida, Arena, Usuario

# Register your models here.
admin.site.register(Time)
admin.site.register(Jogador)
admin.site.register(Partida)
admin.site.register(EstatisticaPartida)
admin.site.register(Arena)
admin.site.register(Usuario)