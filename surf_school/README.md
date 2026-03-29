🌊 Surf School - Sistema de Reservas

Sistema web desenvolvido com Django para gerenciamento de aulas de surf.
Permite que alunos reservem aulas e que administradores gerenciem toda a operação.

🚀 Funcionalidades
👤 Usuário
Cadastro e login
Visualização de aulas disponíveis
Filtros por data, nível e horário
Reserva de aulas
Solicitação de cancelamento
Visualização de reservas
🛠️ Administrador
Criar, editar e excluir aulas
Gerenciar reservas (confirmar/cancelar)
Gerenciar solicitações de cancelamento
🧠 Tecnologias utilizadas
Python
Django
Django REST Framework
SQLite
HTML + CSS
📂 Estrutura do projeto
models.py → lógica de dados
views.py → regras de negócio
templates/ → frontend
static/ → estilos (CSS)
⚙️ Instalação
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente
venv\Scripts\activate   # Windows
# ou
source venv/bin/activate  # Mac/Linux

# Instalar dependências
pip install -r requirements.txt

# Aplicar migrações
python manage.py migrate

# Rodar servidor
python manage.py runserver
🧪 Testes

Para rodar os testes:

python manage.py test
📌 Observações
Projeto focado em backend com Django
Interface simples, priorizando funcionalidade
Sistema pensado para uso real em escolas de surf
📈 Melhorias futuras
Deploy em produção
Integração com pagamento real
Sistema de notificações
Melhorias na interface

👨‍💻 Autor

Lucas Garmendia