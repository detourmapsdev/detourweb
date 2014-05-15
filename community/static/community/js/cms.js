/**
 * Created by PyCharm.
 * User: mauricio
 * Date: 27/02/12
 */
$(document).ready(function(){
    /*$("#id_template").change(function(){
        var template = "";
        var confirmation = confirm("Are you sure to change the template?. Your existent data will be deleted!");
        if (confirmation){
            $("#testimonial_set-group").hide();
        }
        else{

        }
        $("#id_template option:selected").each(function(){

        });
    });*/
    var listCheckBoxes = $(".has_image input[type='checkbox']");
    for(var x = 0; x < listCheckBoxes.length; x++){
        if($(listCheckBoxes[x]).is(":checked")){
            var father = $(listCheckBoxes[x]).parent().parent();
            var has_video = $(father).find(".has_video input").attr("disabled","disabled");
            var video = $(father).find(".video input").attr("disabled","disabled");
        }
        else{
            var father = $(listCheckBoxes[x]).parent().parent();
            var has_video = $(father).find(".has_video input").removeAttr("disabled");
            var video = $(father).find(".video input").removeAttr("disabled");
        }
    }
    var listCheckBoxesVideo = $(".has_video input[type='checkbox']");
    for(var y = 0; y < listCheckBoxesVideo.length; y++){
        if($(listCheckBoxesVideo[y]).is(":checked")){
            var father = $(listCheckBoxesVideo[y]).parent().parent();
            var has_image = $(father).find(".has_image input").attr("disabled","disabled");
            var title = $(father).find(".title input").attr("disabled","disabled");
            var image = $(father).find(".image input").attr("disabled","disabled");
            var link = $(father).find(".link input").attr("disabled","disabled");
        }
        else{
            var father = $(listCheckBoxesVideo[y]).parent().parent();
            var has_image = $(father).find(".has_image input").removeAttr("disabled");
            var title = $(father).find(".title input").removeAttr("disabled");
            var image = $(father).find(".image input").removeAttr("disabled");
            var link = $(father).find(".link input").removeAttr("disabled");
        }
    }
    $(".has_image input[type='checkbox']").click(function(){
        if ($(this).is(":checked")){
            var father = $(this).parent().parent();
            var has_video = $(father).find(".has_video input").attr("disabled","disabled");
            var video = $(father).find(".video input").attr("disabled","disabled");
        }else{
            var father = $(this).parent().parent();
            var has_video = $(father).find(".has_video input").removeAttr("disabled");
            var video = $(father).find(".video input").removeAttr("disabled");
        }
    });
    $(".has_video input[type='checkbox']").click(function(){
        if ($(this).is(":checked")){
            var father = $(this).parent().parent();
            var has_image = $(father).find(".has_image input").attr("disabled","disabled");
            var title = $(father).find(".title input").attr("disabled","disabled");
            var image = $(father).find(".image input").attr("disabled","disabled");
            var link = $(father).find(".link input").attr("disabled","disabled");
        }else{
            var father = $(this).parent().parent();
            var has_image = $(father).find(".has_image input").removeAttr("disabled");
            var title = $(father).find(".title input").removeAttr("disabled");
            var image = $(father).find(".image input").removeAttr("disabled");
            var link = $(father).find(".link input").removeAttr("disabled");
        }
    });
    if($("#id_have_my_own_css").is(":checked")){
        $("#id_my_own_css").removeAttr("disabled");
        $("#id_my_css_file").attr("disabled","disabled");
    }
    else{
        $("#id_my_css_file").attr("disabled","disabled");
        $("#id_my_own_css").removeAttr("disabled");
    }
    $("#id_have_my_own_css").click(function(){
        if ($(this).is(":checked")){
            var father = $(this).parent().parent().next();
            var has_video = $(father).find("#id_my_own_css").attr("disabled","disabled");
            $("#id_my_css_file").removeAttr("disabled");
        }else{
            $("#id_my_css_file").attr("disabled","disabled");
            $("#id_my_own_css").removeAttr("disabled");
        }
    });
})