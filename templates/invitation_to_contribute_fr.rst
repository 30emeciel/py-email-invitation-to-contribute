{% extends "email_base.rst" %}
{% block title %}{% include 'invitation_to_contribute_title_fr.txt' %}{% endblock %}

{% block content %}
Salut {{pax.name}} 🌸


Merci beaucoup pour ta présence avec nous ❤.

{% for kind, items in reservations|groupby("kind") %}
{% if kind == "COLIVING" %}
{% set len_coliving = items|length %}
D'après tes réservations, tu as passé au total {{ len_coliving }} nuit{{ s|pluralize(len_coliving) }} au Coliving au 30ème Ciel.


.. list-table::
   :widths: auto
   :header-rows: 1
   :align: center

   * - Début
     - Fin
     - Nombre de nuits
{%- for r in items %}
   * - {{r.arrival_date|dateformat}}
     - {{r.departure_date|dateformat}}
     - {{r.number_of_nights}}
{% endfor %}

{% else %}
{% set len_coworking = items|length -%}
D'après tes réservations, tu as passé au total {{ len_coworking }} jour{{ len_coworking|pluralize(c) }} de Coworking au 30ème Ciel.

.. list-table::
   :widths: auto
   :header-rows: 1
   :align: center

   * - Date
{%- for r in items %}
   * - {{r.arrival_date|dateformat}}
{% endfor %}

{% endif %}
{% endfor %}

Si tu souhaites contribuer au projet, c'est par ici:
https://www.30emeciel.fr/cc/contributing/

Nous te rappelons que le 30ème Ciel est un lieu à prix libre c'est-à-dire que peu importe le montant de ta contribution, l'important pour nous est que ce soit juste et parfait pour toi ;) Tu peux payer plus ou moins que le montant suggéré.
Quelle que soit ta contribution, nous te remercions de nous aider à faire perdurer ce lieu 🏡 !

Lorsque tu fais ta contribution, il est préférable que tu inscrives ton nom pour que nous puissions plus facilement gérer notre comptabilité :)
{% endblock %}
