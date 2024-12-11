from django.core.management.base import BaseCommand
from times.models import Time, Arena, Jogador
from django.db import connection

class Command(BaseCommand):
    help = "Reseta os IDs da tabela"

    def handle(self, *args, **kwargs):
        # Apague os registros
        Jogador.objects.all().delete()

        # Resete o autoincremento
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='jogador'")

        self.stdout.write(self.style.SUCCESS("IDs da tabela resetados com sucesso!"))
