"""Formularz ContactPage z honeypotem anti-spam."""
from django import forms
from wagtail.contrib.forms.forms import FormBuilder


class HoneypotFormBuilder(FormBuilder):
    """Dokłada ukryte pole-pułapkę. Boty je wypełniają, ludzie nie."""

    @property
    def formfields(self):
        fields = super().formfields
        fields["hp_website"] = forms.CharField(
            required=False,
            widget=forms.HiddenInput(),
        )
        return fields
