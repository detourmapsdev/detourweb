// Support for IE Shit
if (!String.prototype.trim) {
    String.prototype.trim = function () {
        return this.replace(/^\s+|\s+$/g, '');
    }
}

if (!Array.prototype.map) {
    Array.prototype.map = function (callback, thisArg) {
        var T, A, k;
        if (this == null) {
            throw new TypeError(" this is null or not defined");
        }
        var O = Object(this);
        var len = O.length >>> 0;
        if ({}.toString.call(callback) != "[object Function]") {
            throw new TypeError(callback + " is not a function");
        }
        if (thisArg) {
            T = thisArg;
        }
        A = new Array(len);
        k = 0;
        while (k < len) {
            var kValue, mappedValue;
            if (k in O) {
                kValue = O[ k ];
                mappedValue = callback.call(T, kValue, k, O);
                A[ k ] = mappedValue;
            }
            k++;
        }
        return A;
    };
}
$(document).ready(function () {
    /* Rezise */
    function setMapHeight() {
        var height = $(window).height() - $('#map > .tbar').height() - 22;
        $('#map > div > .lbar').height(height);
        $('#map > div > .rbar').height(height);
        $('#detourmap').height(height);
        if ($('#categories').length) {
            height -= $('#categories').height() + 7;
            $('#detourmap').height(height);
        }
    }

    //setMapHeight();
    $(window).resize(function () {
        //setMapHeight();
    });
    /* Menus */
    $('body').click(function () {
        $('.overmenu').remove();
        $('.tbar .active').removeClass('active');
        $("#joinUs a").removeClass("active");
        $("#joinUs a").next().removeClass("overmenuJoin").hide();
        $("#partners a").removeClass("active");
        $("#partners a").next().removeClass("overmenuJoin").hide();
    });
    $('.tmenu').click(function () {
        if ($(this).hasClass('active')) {
            $('.overmenu').remove();
            $(this).removeClass('active');
        } else {
            $('.overmenu').remove();
            $('.tmenu.active').removeClass('active');
            $(this).addClass('active');
            var m = $(this).find('.menu').clone().addClass('overmenu');
            m.addClass('overmenu');
            if ($(this).hasClass('detourmaps')) {
                m.css({'left': 'auto', 'right': 12});
            } else {
                m.css({'left': $(this).position().left, 'min-width': $(this).width() + 60});
            }
            $('.tbar').append(m);
            return false;
        }
    });
    $("#joinUs").click(function (e) {
        if ($(this).hasClass('active')) {
            $('.overmenu').remove();
            $(this).removeClass('active');
        } else {
            $('.overmenu').remove();
            $('.tmenu.active').removeClass('active');
            $(this).addClass('active');
            var m = $(this).find('.menuJoin').clone().addClass('overmenu');
            m.addClass('overmenu');
            if ($(this).hasClass('detourmaps')) {
                m.css({'left': 'auto', 'right': 12});
            } else {
                m.css({'left': $(this).position().left, 'min-width': $(this).width() + 60});
            }
            $('.tbar').append(m);
            e.returnValue = false;
            return false;
        }
    });
    $("#joinUs a").click(function (e) {
        var m = $(this).next();
        if ($(this).hasClass('active')) {
            m.removeClass("overmenuJoin").hide();
            $(this).removeClass('active');
        } else {
            $(this).addClass('active');
            m.addClass('overmenuJoin');
            m.show();
            e.returnValue = false;
            return false;
        }
        e.returnValue = false;
        return false;
    });
    $("#partners a").click(function (e) {
        var m = $(this).next();
        if ($(this).hasClass('active')) {
            m.removeClass("overmenuJoin").hide();
            $(this).removeClass('active');
        } else {
            $(this).addClass('active');
            m.addClass('overmenuJoin');
            m.show();
            e.returnValue = false;
            return false;
        }
        e.returnValue = false;
        return false;
    });
});
