/**
 * Created by PyCharm.
 * User: mauricio
 * Date: 05/12/11
 * Time: 10:46 AM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function(){
    $("#id_url_name").attr("readonly",true);
    $("#id_name").keyup(function(){
        var text = $(this).val();
        var especiales = ["@","|","°","!","#","$","%","&","/","(",")","=","?","¿","¡","*","+","{","}","[","]","`","-",";",",",":",".","ñ","Ñ","<",">","´","'"];
        var evento = window.event;
        var codigoCaracter = evento.charCode || evento.keyCode;
        var caracter = String.fromCharCode(codigoCaracter);
        text = text.replace(/\s/g,"_");
        for(i = 0;i<especiales.length;i++){
            text = text.replace(especiales[i],"_");
        }
        $("#id_url_name").val(text.toLowerCase());
    });
});