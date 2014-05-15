/**
 * User: mauricio
 * Date: 22/11/11
 */

$(document).ready(function(){
    if($("#id_address").length > 0)
        $("#id_address").parent().append("<div id='map' style='width:480px;height:300px;margin: 20px;outline: 1px solid #ccc;'></div>");

    $("#id_geo").attr('readonly',true).height(18).width(345);
    var id_geo = $("#id_geo").val();
    if (id_geo == ""){
        locator();
    }else{
        geometry();
    }
    var latlng = "";
});

var markersArray = [];

function locator(){
    latlng = new google.maps.LatLng(41.847027, -87.755141);
    var myoptionswith={
        zoom:15,
        center:latlng,
        mapTypeId:google.maps.MapTypeId.ROADMAP
    };
    var mapwith = new google.maps.Map(document.getElementById('map'),myoptionswith);



    var markerwith = new google.maps.Marker({
        position : latlng,
        map : mapwith,
        draggable:true
    });
    markersArray.push(markerwith);
    $("#id_address").change(function(){
        var checker = checkHandly();
        if (checker){

        }else{
            updatePosition(map)
        }

    });
    if ($("#id_address").val()){
        var checker = checkHandly();
        if (checker){

        }else{
            updatePosition(map)
        }
    }
    addEvents(markerwith);
    $("input[name='otherLocations']").live("click",function(){
        var lat = parseFloat($(this).attr("idlat"));
        var lng = parseFloat($(this).attr("idlng"));
        var latlng = new google.maps.LatLng(lat,lng);
        checkLocation(map,latlng);
    });
    if (navigator.geolocation){
        navigator.geolocation.getCurrentPosition(function(position){
            var lat = position.coords.latitude;
            var lng = position.coords.longitude;
            latlng = new google.maps.LatLng(lat,lng);
            $("#id_geo").val("POINT(" + lng + " " + lat + ")");
            var myoptions = {
                zoom:15,
                center:latlng,
                mapTypeId:google.maps.MapTypeId.ROADMAP
            };
            var map = new google.maps.Map(document.getElementById('map'),myoptions);

            var marker = new google.maps.Marker({
                position : latlng,
                map : map,
                draggable:true
            });
            console.log(map);
            markersArray.push(marker);

            var cntGoBus = new ControlBusinessHome(map);
            map.controls[google.maps.ControlPosition.TOP_RIGHT].push( cntGoBus.controlDiv );

            var geocoder = new google.maps.Geocoder();
            geocoder.geocode({'latLng':latlng},function(results1,status){
                if(status == google.maps.GeocoderStatus.OK){
                    if(results1[1]){
                        $("#id_address").val(results1[1].formatted_address);
                    }
                }
            });
            $("#id_address").change(function(){
                var checker = checkHandly();
                if (checker){

                }else{
                    updatePosition(map)
                }

            });
            if ($("#id_address").val()){
                var checker = checkHandly();
                if (checker){

                }else{
                    updatePosition(map)
                }
            }
            addEvents(marker);
            $("input[name='otherLocations']").live("click",function(){
                var lat = parseFloat($(this).attr("idlat"));
                var lng = parseFloat($(this).attr("idlng"));
                var latlng = new google.maps.LatLng(lat,lng);
                checkLocation(map,latlng);
            });
        });
    }else{
        alert("hola");
        latlng = new google.maps.LatLng(41.847027, -87.755141);
        var myoptions = {
            zoom:15,
            center:latlng,
            mapTypeId:google.maps.MapTypeId.ROADMAP
        };
        var map = new google.maps.Map(document.getElementById('map'),myoptions);
        var marker = new google.maps.Marker({
            position : latlng,
            map : map,
            draggable:true
        });
        markersArray.push(marker);
        $("#id_address").change(function(){
            var checker = checkHandly();
            if (checker){

            }else{
                updatePosition(map)
            }

        });
        if ($("#id_address").val()){
            var checker = checkHandly();
            if (checker){

            }else{
                updatePosition(map)
            }
        }
        addEvents(marker);
        $("input[name='otherLocations']").live("click",function(){
            var lat = parseFloat($(this).attr("idlat"));
            var lng = parseFloat($(this).attr("idlng"));
            var latlng = new google.maps.LatLng(lat,lng);
            checkLocation(map,latlng);
        });
    }
}

//añadir eventos a los marcadores
function addEvents(marker){
    google.maps.event.addListener(marker,'rightclick',function(){marker.setMap(null);});
    google.maps.event.addListener(marker,'dragstart',function(){});
    google.maps.event.addListener(marker,'drag',function(){});
    google.maps.event.addListener(marker,'dragend',function() {
        var pos = marker.getPosition();
        $("#id_geo").val("POINT(" + pos.lng() + " " + pos.lat() + ")");
        geoPosition(pos);
        var handler = document.getElementById('parentHandly');
        if(!handler) {
            appendCheckHandAddress();
        }
    });
}

function geometry(){
    var id_geo = document.getElementById("id_geo").value;
    var rIdGeo =  id_geo.split(/\(|\)|\s/);
    var lat = parseFloat(rIdGeo[2]);
    var lng = parseFloat(rIdGeo[3]);
    latlng = new google.maps.LatLng(lng,lat);
    var myoptions = {
        zoom:15,
        center:latlng,
        mapTypeId:google.maps.MapTypeId.ROADMAP
    };
    var map = new google.maps.Map(document.getElementById('map'),myoptions);

    var cntGoBus = new ControlBusinessHome(map);
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push( cntGoBus.controlDiv );

    var marker = new google.maps.Marker({
        position : latlng,
        map : map,
        draggable:true
    });
    markersArray.push(marker);
    $("#id_address").change(function(){
        var checker = checkHandly();
        if (checker){

        }else{
            //updatePosition(map)
        }

    });
    if ($("#id_address").val()){
        var checker = checkHandly();
        if (checker){

        }else{
            //updatePosition(map)
        }
    }
    addEvents(marker);
    $("input[name='otherLocations']").live("click",function(){
        var lat = parseFloat($(this).attr("idlat"));
        var lng = parseFloat($(this).attr("idlng"));
        var latlng = new google.maps.LatLng(lat,lng);
        checkLocation(map,latlng);
    });
}

//verificar si existe el campo que contiene el checkbox para la configuración manual
function checkHandly(){
    if($("#parentHandly").length){
        return document.getElementById('handly').checked;
    }else{
        return false;
    }
}

//manejo de los input radio cada vez que se selecciona cambia la ubicación en el mapa y la dirección
function checkLocation(map,pos){
    geoPosition(pos);
    map.setCenter(pos);
    var marker = new google.maps.Marker({map:map,position:pos,draggable:true});
    addEvents(marker);
}

//obtener ubicación desde latlng
function geoPosition(pos){
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({ latLng: pos }, function(responses) {
        if (!checkHandly()) {
            $("#id_address").val(responses[0].formatted_address);
        }
    })
}

//obtener ubicación desde latlng
function checkPosition(pos){
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({
        latLng:pos
    },function(responses){
        var checker = checkHandly();
        if (checker){

        }else{
            $("#id_address").val(responses[0].formatted_address);
        }
        $("#id_geo").val("POINT(" + responses[0].geometry.location.lng() + " " + responses[0].geometry.location.lat() + ")");
    })
}

//añadir div con el checkbox para la configuración manual de la dirección
function appendCheckHandAddress(){
    $("<div style='display: inline-block;margin-left: 20px;' id='parentHandly'><input id='handly' type='checkbox' name='hand' value='1'/>Put the address manually</div>").insertAfter("#id_address")
}

//remover div que contiene el checkbox para ingresar la dirección manualmente
function removeCheckHandAddress(){
    $("#parentHandly").remove();
}

//funcion para actualizar la posición en el mapa, desde el campo address
function clearMarkers(){
    if(markersArray){
        for(i in markersArray){
            markersArray[i].setMap(null);
        }
    }
}

function updatePosition(map){
    $("#optionsLocation").remove();
    clearMarkers();
    var geocoder = new google.maps.Geocoder();
    var address = document.getElementById('id_address').value;
    var position = geocoder.geocode({'address': address},
    function(results,status){
        if(status == google.maps.GeocoderStatus.OK){
            if (status != google.maps.GeocoderStatus.ZERO_RESULTS){
                map.setCenter(results[0].geometry.location);
                $("#id_geo").val("POINT(" + results[0].geometry.location.lng() + " " + results[0].geometry.location.lat() + ")");
                var marker = new google.maps.Marker({map:map,position:results[0].geometry.location,title:results[0].formatted_address,draggable:true});
                markersArray.push(marker);
                var address = "<div id='optionsLocation' style='display: inline-block;padding: 5px;'><h2>You can select these others choices</h2>";
                if (results.length>2){
                    for(i=1;i<results.length;i++){
                        var direccion = results[i].formatted_address;
                        var location = results[i].geometry.location;
                        var lat = results[i].geometry.location.lng();
                        var lng = results[i].geometry.location.lat();
                        address += "<div style='display: inline-block;padding: 2px;'><input type='radio' name='otherLocations' value='" + location + "' idlat='" + lat + "' idlng='" + lng + "'/>" + direccion + "</div>";
                    }
                    address += "</div>";
                    $("#id_address").parent().append(address);
                }
                addEvents(marker);
            }
        }
        else{
            alert("Address incorrect or not exists");
        }
    })
}

var ControlBusinessHome = function(map){
    this.controlDiv = document.createElement("div");
    this.controlDiv.style.marginTop = '5px';
    // Set CSS for the control border
    this.controlUI = document.createElement('DIV');
    this.controlUI.style.height = '18px';
    this.controlUI.style.backgroundColor = 'darkorange';
    this.controlUI.style.borderStyle = 'solid';
    this.controlUI.style.borderWidth = '1px';
    this.controlUI.style.cursor = 'pointer';
    this.controlUI.style.textAlign = 'center';
    this.controlUI.title = 'Click to set the map to Home';
    this.controlDiv.appendChild(this.controlUI);

    // Set CSS for the control interior
    var controlText = document.createElement('DIV');
    controlText.style.fontFamily = 'Arial,sans-serif';
    controlText.style.fontSize = '12px';
    controlText.style.paddingLeft = '4px';
    controlText.style.paddingRight = '4px';
    controlText.innerHTML = 'Go current business';
    this.controlUI.appendChild(controlText);

    // Setup the click event listeners: simply set the map to Chicago
    google.maps.event.addDomListener(this.controlUI, 'click', function() {
        $.getJSON('/communities/business/getitem',{bis:$("#id_business").val()},function(data){
            $("#id_geo").val(data.geo);
            geometry();
            var r = data.geo.slice(7,data.geo.length-1).split(' ') || [];

            var latlng = new google.maps.LatLng(parseFloat(r[1]),parseFloat(r[0]));
            geoPosition(latlng);
        });
    });
};