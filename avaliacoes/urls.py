from django.urls import path
from .views import AvaliacaoListCreateAPIView, AvaliacaoDetailAPIView

app_name = 'avaliacoes_api' # Nome do namespace para a API de avaliações

urlpatterns = [
    path('', AvaliacaoListCreateAPIView.as_view(), name='lista_cria_avaliacao'),
    path('<int:pk>/', AvaliacaoDetailAPIView.as_view(), name='detalhe_avaliacao'),
]
