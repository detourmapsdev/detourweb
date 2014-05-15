{% extends "gis/admin/openlayers.js" %}
{% block base_layer %}new OpenLayers.Layer.Google("Google Base Layer", {'type': google.maps.MapTypeId.ROADMAP, 'sphericalMercator' : true});{% endblock %}
