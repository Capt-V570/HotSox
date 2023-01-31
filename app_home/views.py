from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView
import random

from app_users.validator import HotSoxLogInAndValidationCheckMixin
from app_users.models import User, Sock, SockLike
from .pre_prediction_algorithm import PrePredictionAlgorithm


class HomeView(HotSoxLogInAndValidationCheckMixin, TemplateView):
    model = User

    def get(self, request, *args, **kwargs):
        if request.user.username:
            user = User.objects.get(username=request.user.username)
            user.username = user.username.title()
            context = {"user": user}
        else:
            context = {"user": None}

        return render(request, "app_home/index.html", context)

    def post(self, request, *args, **kwargs):
        pass


class AboutView(TemplateView):
    model = User

    def get(self, request, *args, **kwargs):
        if request.user.username:
            user = User.objects.get(username=request.user.username)
            user.username = user.username.title()
            context = {"user": user}
        else:
            context = {"user": None}

        return render(request, "app_home/about.html", context)

    def post(self, request, *args, **kwargs):
        pass


class SwipeView(HotSoxLogInAndValidationCheckMixin, TemplateView):
    model = User
    template_name = "app_home/swipe.html"

    def get(self, request, *args, **kwargs):
        if request.session.get("sock_pk", None):
            sock = PrePredictionAlgorithm.get_next_sock(
                current_user=User.objects.get(username=request.user.username),
                current_user_sock=get_object_or_404(
                    Sock, pk=request.session["sock_pk"]
                ),
            )
            context = {"sock": sock}
            return render(request, "app_home/swipe.html", context)
        return redirect(reverse("app_users:sock-overview"))

    def post(self, request, *args, **kwargs):
        current_user_sock = get_object_or_404(Sock, pk=request.session["sock_pk"])
        sock_to_be_decided = get_object_or_404(
            Sock, pk=request.POST.get("sock_pk", None)
        )
        if request.POST.get("decision", None) == "like":
            new_sock_like = SockLike(sock=current_user_sock, like=sock_to_be_decided)
            new_sock_like.save()
        else:
            new_sock_dislike = SockLike(
                sock=current_user_sock, dislike=sock_to_be_decided
            )
            new_sock_dislike.save()
        return redirect(reverse("app_home:swipe"))
