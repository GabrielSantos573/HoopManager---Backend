from django.shortcuts import render
from .models import Time, Jogador
from django.http import HttpResponse, JsonResponse
# Create your views here.

from django.http import JsonResponse
from .models import Time

def get_times(request):
    times = Time.objects.all()
    # Lista para armazenar as informações dos times
    times_list = []

    # Iterando sobre os times
    for time in times:
        # Obtém os jogadores associados ao time
        jogadores = time.jogadores.all()

        # Lista para armazenar os jogadores de cada time
        jogadores_list = []
        for jogador in jogadores:
            # Adiciona os detalhes do jogador à lista
            jogadores_list.append({
                'nome': jogador.nome,
                'posicao': jogador.get_posicao_display(),
                'altura': str(jogador.altura),  # Para garantir que será serializável
                'pontos': jogador.pontos,
                'rebotes': jogador.rebotes,
                'assistencias': jogador.assistencias,
                'turnovers': jogador.turnovers,
                'roubos_bola': jogador.roubos_bola,
            })

        # Adiciona os detalhes do time e seus jogadores à lista de times
        times_list.append({
            'nome': time.nome,
            'regiao': time.regiao,
            'treinador': time.treinador,
            'numero_jogadores': time.numero_jogadores,
            'vitorias': time.vitorias,
            'derrotas': time.derrotas,
            'campeonatos_vencidos': time.campeonatos_vencidos,
            'jogadores': jogadores_list  # Jogadores associados ao time
        })

    # Retorna os times e jogadores associados como resposta JSON
    return JsonResponse(times_list, safe=False)
