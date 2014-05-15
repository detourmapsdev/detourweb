/**
 * User: Juan Manuel Ticona Pacheco
 * Date: 5/09/2012
 */

(function ($) {
    $.fn.jslider = function () {

        var snap_left = document.createElement('span');
        snap_left.setAttribute('class', 'snap_slider');
        snap_left.style['left'] = '0';
        var snap_right = document.createElement('span');
        snap_right.setAttribute('class', 'snap_slider');
        snap_right.style['right'] = '0';

        var img_snap_left = document.createElement('img');
        img_snap_left.setAttribute('src', '/static/community/img/left-knob.png');
        var img_snap_right = document.createElement('img');
        img_snap_right.setAttribute('src', '/static/community/img/right-knob.png');

        snap_left.appendChild(img_snap_left);
        snap_right.appendChild(img_snap_right);

        snap_left.style['top'] = ((this.height() / 2) + ($(snap_left).height() / 2)) + "px";
        snap_right.style['top'] = ((this.height() / 2) + ($(snap_left).height() / 2)) + "px";

        var frames = this.find("div.frame");
        frames.hide();
        $(snap_left).click(function () {
            for (var j = frames.length - 1; j > -1; j--) {
                if (frames[j].style['display'] != 'none') {
                    frames[j].style['display'] = 'none';
                    var index = 0;
                    if ((j - 1) < 0) {
                        index = frames.length - 1;
                    } else {
                        index = j - 1;
                    }
                    frames[index].style['display'] = 'inline-block';
                    return false;
                }
            }
        });
        $(snap_right).click(function () {
            for (var j = 0; j < frames.length; j++) {
                if (frames[j].style['display'] != 'none') {
                    frames[j].style['display'] = 'none';
                    var index = 0;
                    if ((j + 1) > (frames.length - 1)) {
                        index = 0;
                    } else {
                        index = j + 1;
                    }
                    frames[index].style['display'] = 'inline-block';
                    return false;
                }
            }
        });
        $(frames[0]).show();

        this.append(snap_left);
        this.append(snap_right);
    }
})(jQuery);

(function ($) {
    $.fn.jmtpValidate = function (options) {
        var settings = {
        };
        var _this = this;
        $.extend(settings, options);
        var value = this.val();
        if (settings.type === 'email') {
            var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            return re.test(value);
        } else {
            return null;
        }

    }
})(jQuery);

function jmtpReSendActivateMail(options) {
    if (options.email == undefined) throw("Less the email.");
    options['preSend']();
    $.getJSON('/user/re-send-activation-mail',
        {user_email: options.email}, function (data) {

            options['postSend'](data);
            return data;
        });
}


$(document).ready(function () {
    // TopBar Nav Hover & Menus!
    $('.tbar nav ul li a').click(function (e) {
        e.preventDefault();
        var href = $(this).attr("href");
        document.location.href = href;
    });
    $('.tbar nav ul li a').hover(function () {
        $(this).addClass('h');
        function navIn(overnav) {
            if ($(overnav).hasClass('h')) {
                $('.overmenu').remove();
                $('.tmenu.active').removeClass('active');
                $(overnav).addClass('hover');
                //$($(overnav).attr('href')).addClass('display');
            }
        }

        if ($.browser.msie) {
            navIn(this);
        } else {
            setTimeout(navIn, 150, this);
        }
    }, function () {
        $(this).removeClass('h');
        function navOut(overnav) {
            var c = $($(overnav).attr('href'));
            if (!c.hasClass('h')) {
                c.removeClass('display');
                $(overnav).removeClass('hover');
            }
        }

        if ($.browser.msie) {
            navOut(this);
        } else {
            setTimeout(navOut, 150, this);
        }
    });
    $('#map > .over').hover(function () {
        $(this).addClass('h');
    }, function () {
        $(this).removeClass('h');
        setTimeout(function (overnav) {
            if (!$(overnav).hasClass('h')) {
                $(overnav).removeClass('display');
                $('.tbar nav ul li a[href="#' + $(overnav).attr('id') + '"]').removeClass('hover');
            }
        }, 250, this);
    });
    $(".login").hover(function(){
		submenu = $("ul." + $(this).attr("name"));
		submenu.show();
	}, function() {
		submenu.hover(function(){
			$(this).show();
		},function(){
			$(this).hide();
		});
		submenu.hide();
	});
});