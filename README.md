# Sistema de Gerenciamento de Basquete

Este é um projeto Django para gerenciamento de equipes e jogadores de basquete, permitindo o cadastro e visualização de times e seus jogadores, com funcionalidades específicas para controle de acessos e estatísticas.

Clone o repositório para sua máquina local: 
`git clone <URL_DO_REPOSITORIO> && cd <NOME_DO_DIRETORIO_DO_PROJETO>`. 

Para manter as dependências do projeto isoladas, crie e ative um ambiente virtual com 

`python -m venv venv` e ative-o com `source venv/bin/activate` (no Windows, use `venv\Scripts\activate`).

Instale as dependências listadas no arquivo `requirements.txt` com `pip install -r requirements.txt`.

Para criar as tabelas no banco de dados, execute `python manage.py makemigrations && python manage.py migrate`. 

Em seguida, crie um superusuário para acessar o painel administrativo do Django com `python manage.py createsuperuser`.

Agora, com tudo configurado, inicie o servidor de desenvolvimento com `python manage.py runserver`. 

O servidor estará disponível em [http://localhost:8000](http://localhost:8000). 

### Funcionalidades Principais

Cadastro de Times e Jogadores, Autenticação e Controle de Acesso com JWT e Filtragem e Consulta de Dados de Times e Jogadores.

---

### Autor

Desenvolvido por **Gustavo Maxwel de Sousa Oliveira e Gabriel Oliveira Santos**. Entre em contato para dúvidas ou sugestões de melhoria!
