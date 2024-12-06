from django.shortcuts import render
from django.http import JsonResponse
from .models import Time, Jogador, Arena, Partida, EstatisticaPartida
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def get_times(request):
    # Otimizando as consultas com prefetch_related para evitar N+1 problem
    times = Time.objects.prefetch_related('jogador_set')

    # Lista para armazenar os detalhes dos times
    times_list = []

    for time in times:
        # Jogadores associados ao time
        jogadores_list = [
            {
                'id': jogador.id,
                'nome': jogador.nome,
                "idade": jogador.idade,
                'posicao': jogador.get_posicao_display(),
                'status': jogador.get_status_display(),
                'altura': str(jogador.altura),
                'pontos': jogador.pontos,
                'rebotes': jogador.rebotes,
                'assistencias': jogador.assistencias,
                'turnovers': jogador.turnovers,
                'roubos_bola': jogador.roubos_bola,
                'num_jogos': jogador.num_jogos,
                'foto': jogador.foto.url if jogador.foto else None,
            }
            for jogador in time.jogador_set.all()
        ]

        # Arena associada ao time (verificando se existe)
        arena = getattr(time, 'arena', None)  # Evita o erro ao acessar uma arena inexistente
        arena_details = {
            'nome': arena.nome if arena else None,
            'local': arena.local if arena else None,
            'capacidade': arena.capacidade if arena else None,
        }

        # Adiciona o time e seus detalhes à lista
        times_list.append({
            'id': time.id,
            'nome': time.nome,
            'regiao': time.regiao,
            'treinador': time.treinador,
            'numero_jogadores': time.num_jogadores,
            'vitorias': time.vitorias,
            'derrotas': time.derrotas,
            'campeonatos_vencidos': time.campeonatos_vencidos,
            'descricao':time.descricao,
            'logo': time.logo.url if time.logo else None,  # URL completa da logo
            'jogadores': jogadores_list,
            'arena': arena_details
        })

    # Retorna os dados em formato JSON
    return JsonResponse(times_list, safe=False)

@csrf_exempt
def get_jogadores(request, time_id):
    jogadores = Jogador.objects.filter(time_id=time_id)
    jogadores_list = [
        {
            'id': jogador.id,
                'nome': jogador.nome,
                "idade": jogador.idade,
                'posicao': jogador.get_posicao_display(),
                'status': jogador.get_status_display(),
                'altura': str(jogador.altura),
                'pontos': jogador.pontos,
                'rebotes': jogador.rebotes,
                'assistencias': jogador.assistencias,
                'turnovers': jogador.turnovers,
                'roubos_bola': jogador.roubos_bola,
                'num_jogos': jogador.num_jogos,
                'foto': jogador.foto.url if jogador.foto else None,
        }
        for jogador in jogadores
    ]
    return JsonResponse(jogadores_list, safe=False)

@csrf_exempt
def create_time (request):
    if request.method == "POST":
        try:
            data = request.POST  # Dados textuais enviados no FormData
            jogadores = json.loads(data.get("jogadores", "[]"))  # Array de jogadores no formato JSON

            # Validação de campos obrigatórios
            if not data.get("nome") or not data.get("regiao") or not data.get("numero_jogadores"):
                return JsonResponse({"error": "Campos obrigatórios estão faltando: nome, regiao ou numero_jogadores."}, status=400)

            # Criação do time
            time = Time.objects.create(
                nome=data.get("nome"),
                regiao=data.get("regiao"),
                treinador=data.get("treinador"),
                descricao=data.get("descricao"),
                num_jogadores=int(data.get("numero_jogadores", 0)),
                logo=request.FILES.get("logo"),  # Logo enviado como arquivo
            )

            # Criação dos jogadores associados ao time
            for jogador_data in jogadores:
                Jogador.objects.create(
                    nome=jogador_data.get("nome"),
                    idade=jogador_data.get("idade"),
                    posicao=jogador_data.get("posicao"),
                    status=jogador_data.get("status"),
                    altura=jogador_data.get("altura"),
                    foto=request.FILES.get("foto"),  # Foto enviada como arquivo
                    time=time,  # Associação com o time recém-criado
                )

            return JsonResponse({"message": "Time e jogadores criados com sucesso!"}, status=201)
        except Exception as e:
            return JsonResponse({"error": f"Erro ao criar time e jogadores: {str(e)}"}, status=400)
    else:
        return JsonResponse({"error": "Método não permitido"}, status=405)
