/**
 * Created with PyCharm.
 * User: root
 * Date: 15/06/13
 * Time: 11:06 AM
 * To change this template use File | Settings | File Templates.
 */
$(document).ready(function () {
    var cmData = $("li.allData");
    $("input[name='q']").keyup(function () {
        if (!cmData) {
            new Messi("Wait please ..  building map, try it again!", {title: 'DetourMaps - Alert System', modal: true});
        } else {
            if ($(this).val() !== " ") {
                $(cmData).hide();
                $("#left_bar").css("overflow", "visible");
                var listSimilar = new Array();
                for (var i = 0; i < cmData.length; i++) {
                    var texto = $(cmData[i]).find("a").text().toLowerCase();
                    if (texto.indexOf($(this).val().toLowerCase()) != -1) {
                        $(cmData[i]).show();
                    }
                }
                var controlHeight = $("#displayResults").height();
                if (parseInt(controlHeight) == 0) {
                    var heightFooter = $("#homeFooter_cnt").position();
                    var realHeight = heightFooter.top - ($(".tbar").height() + $(".bars_container").height());
                    $("#displayResults").animate({"height": realHeight});
                    $("#displayResults .cat-list").css({"height": realHeight});
                }
            }
        }
    });
    $("li.cat").click(function () {
        if (!cmData) {
            new Messi("Wait please ..  building map, try it again!", {title: 'DetourMaps - Alert System', modal: true});
        } else {
            $("#left_bar").css("overflow", "visible");
            var splitindice = $(this).attr("id");
            $(cmData).hide();
            for (var i = 0; i < cmData.length; i++) {
                if($(cmData[i]).hasClass(splitindice)){
                    $(cmData[i]).show();
                }
            }
            var controlHeight = $("#displayResults").height();
            if (parseInt(controlHeight) == 0) {
                var heightFooter = $("#homeFooter_cnt").position();
                var realHeight = heightFooter.top - ($(".tbar").height() + $(".bars_container").height());
                $("#displayResults").animate({"height": realHeight});
                $("#displayResults .cat-list").css({"height": realHeight});
            }
        }
    });
});