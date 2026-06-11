"""Rejestracja Przewodnika moderatora w panelu Wagtail: URL + pozycja w menu głównym."""
from django.urls import path, reverse_lazy
from wagtail import hooks
from wagtail.admin.menu import MenuItem

from apps.guide import views


@hooks.register("register_admin_urls")
def register_guide_url():
    return [path("przewodnik/", views.handbook, name="guide_handbook")]


@hooks.register("register_admin_menu_item")
def register_guide_menu_item():
    return MenuItem(
        "Przewodnik moderatora",
        reverse_lazy("guide_handbook"),
        icon_name="help",
        order=10000,
    )
