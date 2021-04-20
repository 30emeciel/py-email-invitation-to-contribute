{% extends "email_base.rst" %}
{% block title %}{% include 'invitation_to_contribute_title_fr.txt' %}{% endblock %}

{% block content %}
Salut {{pax.name}} 🌸


Si tu reçois ce mail c'est que tu as passé 1 ou plusieurs nuits au 30ème Ciel ☺
Merci beaucoup pour ta présence avec nous ❤.

D'après tes réservations, tu as passé {{request.number_of_nights}} nuits au 30ème Ciel.
Si tu souhaites contribuer au projet, c'est par ici:
https://www.30emeciel.fr/cc/contributing/

Nous te rappelons que le 30ème Ciel est un lieu à prix libre c'est-à-dire que peu importe le montant de ta contribution, l'important pour nous est que ce soit juste et parfait pour toi ;) Tu peux payer plus ou moins que le montant suggéré.
Quelle que soit ta contribution, nous te remercions de nous aider à faire perdurer ce lieu 🏡 !

Lorsque tu fais ta contribution, il est préférable que tu inscrives ton nom pour que nous puissions plus facilement gérer notre comptabilité :)
{% endblock %}
