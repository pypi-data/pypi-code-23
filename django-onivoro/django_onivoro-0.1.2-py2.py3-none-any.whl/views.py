# coding: utf-8
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now
from .forms import FonteExternaForm
from .models import FonteExterna
from .sincronizador import Sincronizador


@login_required
def home_fonte_externa(request):
    fontes_recentes = FonteExterna.objects.all()[:5].select_related()
    return render(request, "onivoro/home.html", {"fontes": fontes_recentes})


@login_required
def criar_fonte_externa(request):
    form = FonteExternaForm(request.POST or None)

    if form.is_valid():

        externa = form.save(commit=False)
        externa.criado_em = now()
        externa.atualizado_em = now()
        externa.save()

        return redirect("detalhe_fonte_externa", id=externa.id)

    else:
        return render(request, "onivoro/criar.html", {"form": form})


@login_required
def detalhe_fonte_externa(request, id):
    fonte = get_object_or_404(FonteExterna, id=id)
    dados_importados = fonte.ref_modelo.objects.all()[:5]

    contador_importados = fonte.ref_modelo.objects.all().count()

    # camada = CamadaGeoJSON.objects.get(app=fonte.app, modelo=fonte.modelo)
    camada = "" # TODO resolver isto

    dicionario = {"fonte": fonte,
                  "camada": camada,
                  "dados_importados": dados_importados,
                  "contador_importacao": contador_importados}

    return render(request, "onivoro/detalhe.html", dicionario)


@login_required
def editar_fonte_externa(request, id):
    instancia = get_object_or_404(FonteExterna, pk=id)
    form = FonteExternaForm(request.POST or None, instance=instancia)

    if form.is_valid():

        externa = form.save(commit=False)
        externa.criado_em = now()
        externa.atualizado_em = now()
        externa.save()
        return redirect("detalhe_fonte_externa", id=externa.id)

    else:
        return render(request, "onivoro/editar.html", {"form": form})


@login_required
def excluir_fonte_externa(request, id):
    instancia = get_object_or_404(FonteExterna, pk=id)

    if request.POST:

        instancia.delete()
        return render(request, "onivoro/excluir.html", {})
    else:

        return redirect("home_fonte_externa")


@login_required
def sincronizar_fonte_externa(request, id):
    fonte = get_object_or_404(FonteExterna, pk=id)

    sync = Sincronizador(fonte)
    sucesso = sync.sincronizar()

    return render(request, "onivoro/sincronizado.html", {"fonte_externa": fonte, "sucesso": sucesso})


@login_required
def lista_fonte_externa(request):
    pass