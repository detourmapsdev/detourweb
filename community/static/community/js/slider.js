/**
 * Created by PyCharm.
 * User: mauricio
 * Date: 14/12/11
 * Time: 09:46 AM
 * To change this template use File | Settings | File Templates.
 */
var rockandroll;
var stopRock = function(){return false;};
var startRock = function(){return false;};

(function($){
    $.fn.slider = function(opciones){
        var settings = {
            width: 0,
            height: 0,
            speed: 2000,
            speedSlide: 500
        };
        $.extend(settings,opciones);
        this.each(function(){
            var divSlider = $(this);
            var arrayImgSlider = []
            arrayImgSlider = divSlider.find("div.img-wrap img");
            if(arrayImgSlider.length <= 1){

            }else{
                rockandroll = setInterval(function(){
                    divSlider.find("div.img-wrap").animate({
                        "left": "-=215"
                    },settings.speedSlide,function(){
                        divSlider.find("div.img-wrap").css({
                            "left": "0"
                        });
                        divSlider.find("div.img-wrap img:last").after(divSlider.find("div.img-wrap img:first"));
                    });
                },settings.speed);
                stopRock = function stopRockAndRoll(){
                    clearInterval(rockandroll);
                };
                startRock = function startRockAndRoll(){
                    rockandroll = setInterval(function(){
                        divSlider.find("div.img-wrap").animate({
                            "left": "-=215"
                        },settings.speedSlide,function(){
                            divSlider.find("div.img-wrap").css({
                                "left": "0"
                            });
                            divSlider.find("div.img-wrap img:last").after(divSlider.find("div.img-wrap img:first"));
                        });
                    },settings.speed);
                };
            }
        });
    }
})(jQuery);