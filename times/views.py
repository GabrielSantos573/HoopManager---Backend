from django.shortcuts import render
from django.http import JsonResponse
from .models import Time, Jogador, Arena, Partida, EstatisticaPartida
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import json
import traceback

@csrf_exempt
def get_times(request):
    times = Time.objects.prefetch_related('jogador_set').select_related('arena')

    times_list = []
    for time in times:
        jogadores_list = [
            {
                'id': jogador.id,
                'nome': jogador.nome,
                'idade': jogador.idade,
                'posicao': jogador.get_posicao_display(),
                'status': jogador.get_status_display(),
                'altura': str(jogador.altura),
                'peso': str(jogador.peso),
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

        arena = getattr(time, 'arena', None)
        arena_details = {
            'nome': arena.nome if arena else None,
            'local': arena.local if arena else None,
            'capacidade': arena.capacidade if arena else None,
        }

        times_list.append({
            'id': time.id,
            'nome': time.nome,
            'regiao': time.get_regiao_display(),
            'endereco': time.endereco,
            'treinador': time.treinador,
            'numero_jogadores': time.num_jogadores,
            'vitorias': time.vitorias,
            'derrotas': time.derrotas,
            'descricao': time.descricao,
            'logo': time.logo.url if time.logo else None,
            'jogadores': jogadores_list,
            'arena': arena_details
        })

    return JsonResponse(times_list, safe=False)

@csrf_exempt
def get_jogadores(request, time_id):
    jogadores = Jogador.objects.filter(time_id=time_id)
    jogadores_list = [
        {
            'id': jogador.id,
            'nome': jogador.nome,
            'idade': jogador.idade,
            'posicao': jogador.get_posicao_display(),
            'status': jogador.get_status_display(),
            'altura': str(jogador.altura),
            'peso': str(jogador.peso),
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
def create_time(request):
    if request.method == "POST":
        try:
            # Verifica se já existe um time cadastrado
            if Time.objects.exists():
                return JsonResponse({"error": "Já existe um time cadastrado. Apenas um time é permitido."}, status=400)

            data = request.POST  # Dados textuais enviados no FormData
            jogadores = json.loads(data.get("jogadores", "[]"))  # Array de jogadores no formato JSON

            # Validação de campos obrigatórios para o time
            if not data.get("nome") or not data.get("regiao") or not data.get("numero_jogadores"):
                return JsonResponse({"error": "Campos obrigatórios do time estão faltando: nome, regiao ou numero_jogadores."}, status=400)

            # Validação de campos obrigatórios para a arena
            if not data.get("arena_nome") or not data.get("arena_local") or not data.get("arena_capacidade"):
                return JsonResponse({"error": "Campos obrigatórios da arena estão faltando: arena_nome, arena_local ou arena_capacidade."}, status=400)

            # Conversões de tipos
            try:
                numero_jogadores = int(data.get("numero_jogadores", 0))
                arena_capacidade = int(data.get("arena_capacidade", 0))
            except ValueError:
                return JsonResponse({"error": "Número de jogadores ou capacidade da arena deve ser um valor numérico válido."}, status=400)

            # Criação do time
            time = Time.objects.create(
                nome=data.get("nome"),
                regiao=data.get("regiao"),
                endereco=data.get("endereco"),
                treinador=data.get("treinador"),
                descricao=data.get("descricao"),
                num_jogadores=numero_jogadores,
                logo=request.FILES.get("logo", None),  # Logo enviada como arquivo
            )

            # Criação da arena associada ao time
            Arena.objects.create(
                nome=data.get("arena_nome"),
                local=data.get("arena_local"),
                capacidade=arena_capacidade,
                time=time,  # Associação com o time recém-criado
            )

            # Criação dos jogadores associados ao time
            for jogador_data in jogadores:
                try:
                    idade = int(jogador_data.get("idade", 0))
                    altura = float(jogador_data.get("altura", 0))
                    peso = float(jogador_data.get("peso", 0))
                except ValueError:
                    return JsonResponse({"error": "Idade, altura ou peso de um jogador é inválido."}, status=400)

                Jogador.objects.create(
                    nome=jogador_data.get("nome"),
                    idade=idade,
                    posicao=jogador_data.get("posicao"),
                    status=jogador_data.get("status"),
                    altura=altura,
                    peso=peso,
                    foto=request.FILES.get("foto", None),  # Foto enviada como arquivo
                    time=time,  # Associação com o time recém-criado
                )

            return JsonResponse({"message": "Time, jogadores e arena criados com sucesso!"}, status=201)
        except Exception as e:
            return JsonResponse({"error": f"Erro ao criar time, jogadores ou arena: {str(e)}"}, status=400)
    else:
        return JsonResponse({"error": "Método não permitido"}, status=405)

@csrf_exempt
def create_partida(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Obtém e valida os dados necessários
            arena_id = data.get("arena_id")
            if not arena_id:
                return JsonResponse({"error": "É necessário selecionar uma arena."}, status=400)

            arena = Arena.objects.get(id=arena_id)
            time = arena.time  # Time associado à arena

            # Time adversário deve ter apenas o nome
            time_adversario = data.get("time_adversario")
            if not time_adversario:
                return JsonResponse({"error": "É necessário informar o nome do time adversário."}, status=400)

            # Criação da partida
            partida = Partida.objects.create(
                data=data.get("data"),
                arena=arena,
                status=data.get("status"),
                time=time,
                time_adversario=time_adversario,
            )

            return JsonResponse({"message": "Partida criada com sucesso!", "id": partida.id}, status=201)
        except Arena.DoesNotExist:
            return JsonResponse({"error": "A arena selecionada não existe."}, status=404)
        except Exception as e:
            return JsonResponse({"error": f"Erro ao criar partida: {str(e)}"}, status=400)
    else:
        return JsonResponse({"error": "Método não permitido"}, status=405)


@csrf_exempt
def get_partidas(request):
    if request.method == "GET":
        # Consulta todas as partidas com suas relações
        partidas = Partida.objects.select_related('arena', 'time')

        partidas_list = []
        for partida in partidas:
            partidas_list.append({
                'id': partida.id,
                'data': partida.data.strftime("%Y-%m-%d %H:%M:%S"),
                'status': partida.get_status_display() if partida.status else "Não Definido",
                'arena': {
                    'id': partida.arena.id,
                    'nome': partida.arena.nome,
                    'local': partida.arena.local,
                    'capacidade': partida.arena.capacidade,
                } if partida.arena else None,
                'time': {
                    'id': partida.time.id,
                    'nome': partida.time.nome,
                    'treinador': partida.time.treinador,
                    'logo': partida.time.logo.url if partida.time.logo else None,
                } if partida.time else None,
                'time_adversario': partida.time_adversario,
                'placar_time_casa': partida.placar_time_casa,
                'placar_time_visitante': partida.placar_time_visitante,
            })

        return JsonResponse(partidas_list, safe=False)
    else:
        return JsonResponse({"error": "Método não permitido"}, status=405)

