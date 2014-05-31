var detourmaps = {};
window['detourmaps'] = detourmaps;

detourmaps['eventBubble'] = undefined;
detourmaps['tabEvent'] = undefined;
detourmaps['businessEventsList'] = undefined;

// Estilos del mapa
var dtmStyle = [
    {
        featureType: "road",
        elementType: "geometry",
        stylers: [
            { hue: "#00ccff" },
            { saturation: -55 },
            { lightness: -35 },
            { gamma: 2 },
            { visibility: "simplified" }
        ]
    },
    {
        featureType: "road",
        elementType: "labels",
        stylers: [
            { hue: "#00ccff" },
            { saturation: -55 },
            { lightness: -5 },
            { gamma: 1 }
        ]
    },
    {
        featureType: "landscape",
        stylers: [
            { lightness: 50 }
        ]
    },
    {
        featureType: "poi.park",
        stylers: [
            { lightness: 10 },
            { saturation: 0 },
            { gamma: 1.5 }
        ]
    },
    {
        featureType: "poi.place_of_worship",
        stylers: [
            { visibility: "off" }
        ]
    },
    {
        featureType: "landscape.man_made",
        stylers: [
            { visibility: "off" }
        ]
    }
];

var bubble = undefined;
// Slider
var rockandroll;
var stopRock = function () {
    return false;
};
var startRock = function () {
    return false;
};
var notOverMarker = true;

(function ($) {
    $.fn.slider = function (opciones) {
        var settings = {
            width: undefined,
            height: undefined,
            speed: 2000,
            speedSlide: 500,
            animate_id: undefined,
            img_index: 0
        };
        var _this = this;
        $.extend(settings, opciones);
        if (settings.width == undefined & settings.height == undefined) {
            settings.width = this.find('img').width();
            settings.height = this.find('img').height();
        }

        this.css('overflow', 'hidden');
        this.css('width', (settings.width).toString() + 'px');
        this.css('height', (settings.height).toString() + 'px');
        this.css('position', 'relative');

        this.find("img").each(function (index, obj) {
            obj.style.width = (settings.width).toString() + "px";
            obj.style.height = (settings.height).toString() + "px";

            obj.style.position = "absolute";
            obj.style.left = (settings.width * index).toString() + "px";
            obj.style.top = "0";
        });
        this.mouseenter(function () {
            clearInterval(settings.animate_id);
            settings.animate_id = undefined;
        });

        this.mouseout(function () {
            if (settings.animate_id != undefined) return false;
            settings.animate_id = setInterval(function () {
                if (settings.img_index == (_this.find("img").length - 1)) {
                    settings.img_index = 0;
                } else {
                    settings.img_index++;
                }
                if (_this.find("img").length > 1) animate();
            }, settings.speed);
        });
        function animate() {
            _this.find("img").animate({
                    left: "-=" + (settings.width).toString()
                }, settings.speedSlide,
                function () {
                    var list_img = _this.find("img");
                    var curr_index = settings.img_index;
                    var contX = 0;
                    for (var i = 0; i < list_img.length; i++) {
                        $(list_img[curr_index]).css('left', (settings.width * i).toString() + 'px');
                        if (curr_index >= list_img.length - 1) curr_index = 0;
                        else curr_index++;
                    }
                });
        }

        settings.animate_id = setInterval(function () {
            if (settings.img_index == (_this.find("img").length - 1)) {
                settings.img_index = 0;
            } else {
                settings.img_index++;
            }
            if (_this.find("img").length > 1) animate();
        }, settings.speed);
    }

})(jQuery);

function urlChanger(iden, biz, tab) {
    if (typeof window.history.pushState == 'function') {
        if(tab.subtab){
            window.history.replaceState({biz: iden, url: "/communities/" + biz.community + "/map/business/?name=" + biz.url_name + "&auth_code=" + biz.auth_code + "&tab=" + tab.tab+ "|" + tab.subtab}, biz.auth_code, "/communities/" + biz.community + "/map/business/?name=" + biz.url_name + "&auth_code=" + biz.auth_code + "&tab=" + tab.tab + "|" + tab.subtab);
            //window.location.hash = "#!/" + urlPath;
            window.history.pushState(iden, "Titulo", "/communities/" + biz.community + "/map/business/?name=" + biz.url_name + "&auth_code=" + biz.auth_code + "&tab=" + tab.tab + "|" + tab.subtab);
        }
        else{
            window.history.replaceState({biz: iden, url: "/communities/" + biz.community + "/map/business/?name=" + biz.url_name + "&auth_code=" + biz.auth_code + "&tab=" + tab.tab}, biz.auth_code, "/communities/" + biz.community + "/map/business/?name=" + biz.url_name + "&auth_code=" + biz.auth_code + "&tab=" + tab);
            //window.location.hash = "#!/" + urlPath;
            window.history.pushState(iden, "Titulo", "/communities/" + biz.community + "/map/business/?name=" + biz.url_name + "&auth_code=" + biz.auth_code + "&tab=" + tab.tab);
        }
    } else {
        if(tab.subtab){
            window.history.pushState(iden, "Titulo", "/communities/" + biz.community + "/map/business/?name=" + biz.url_name + "&auth_code=" + biz.auth_code + "&tab=" + tab.tab + "|" + tab.subtab);
        }
        else{
            window.history.pushState(iden, "Titulo", "/communities/" + biz.community + "/map/business/?name=" + biz.url_name + "&auth_code=" + biz.auth_code + "&tab=" + tab.tab);
        }

    }
}

var tab_review;
var lhash = undefined;
var bisInfo;
$(document).ready(function () {

    if (window.location.hash) {
        lhash = window.location.hash;
    }
    var ci, bi, bb;
    var tab_info_title = 'INFO';
    var tab_rating_title = 'VIDEO';
    var tab_review_title = 'REVIEW';
    bisInfo = new InfoBubble({
        borderRadius: 8,
        minWidth: 423,
        minHeight: 185
    });
    bubble = bisInfo;
    bisInfo.addTab(tab_info_title, relleno());
    bisInfo.tabs_[0].tab.removeAttribute('style');
    $(bisInfo.tabs_[0].tab).addClass('tab_info');
    $(bisInfo.tabs_[0].tab).addClass('tab_1');
    $(bisInfo.tabs_[0].tab).click(function () {
        $(bisInfo.tabs_[1].content).find('#tab_video_coupon').hide();
        $(bisInfo.tabs_[0].content).find('#tab_video_pnl01').hide();
    });
    var bitbybit = 1;
    var flagcontrol = false;
    $(document).on("click", "a.fup", function(event){
        event.preventDefault();
        if(flagcontrol == false){
            --bitbybit;
            $("#wrap-vertical-slider").css("transform","translateY("+bitbybit * -374+"px)");
        }
        else{
            bitbybit = bitbybit - 2;
            $("#wrap-vertical-slider").css("transform","translateY("+bitbybit * -374+"px)");
        }
        flagcontrol = false;
    });
    $(document).on("click", "a.fdown", function(event){
        event.preventDefault();
        if(bitbybit == 1){
            $("#wrap-vertical-slider").css("transform","translateY("+bitbybit * -374+"px)");
            bitbybit++;
        }else{
            if(flagcontrol){
                $("#wrap-vertical-slider").css("transform","translateY("+bitbybit * -374+"px)");
                bitbybit++;
            }else{
                bitbybit = bitbybit + 1;
                $("#wrap-vertical-slider").css("transform","translateY("+bitbybit * -374+"px)");
                bitbybit++;
            }
        }
        flagcontrol = true;
    });
    $(document).on("click", "a.couponPop", function(event){
        event.preventDefault();
        $(this).magnificPopup({
          type: 'image'
            // other options
        });
    });
    $(document).on("click", "#textMenu ul li", function(){
        $("#textMenu ul li").not($(this)).css("background","#fff  url(/static/community/evolution/icon-view-menu.png) center right no-repeat").css("color","#666");
        $(this).css("background", "#f48031 url(/static/community/evolution/icon-active-view-menu.png) center right no-repeat").css("color", "#fff");
        $("div#show-dish").html("");
        var listImg = $(this).find("img.thumb");
        if(listImg.length > 1){
            $("div#nav-dishes").show();
            for(var j=0; j<listImg.length; j++){
                if(j==0){
                    $(listImg[j]).clone().appendTo("div#show-dish").show();
                }else{
                    $(listImg[j]).clone().appendTo("div#show-dish").hide();
                }
            }
        }else{
            $("div#nav-dishes").hide();
            $(this).find("img.thumb").clone().appendTo("div#show-dish").show();
        }
        //$(this).find("img.thumb").clone().appendTo("div#show-dish").show();
        $(this).find("b").clone().appendTo("div#show-dish").show();
        $("div#show-dish").append($(this).contents().first().text());
    });
    var xs = 1;
    $(document).on("click", "a.mnav", function(e){
        e.preventDefault();
        var listIMG = $("div#show-dish img.thumb");
        if($(this).hasClass("left-nav-dish")){
            if(xs==1){
                $(listIMG[xs-1]).hide();
                $(listIMG[listIMG.length -1]).fadeIn();
                xs=listIMG.length;
            }else{
                $(listIMG[xs-1]).hide();
                --xs;
                $(listIMG[xs-1]).fadeIn();
            }
        }else{
            if(xs==listIMG.length){
                $(listIMG[xs-1]).hide();
                $(listIMG[0]).fadeIn();
                xs=1;
            }else{
                $(listIMG[xs-1]).hide();
                $(listIMG[xs]).fadeIn();
                xs++
            }
        }
    });
    if (varDetourmaps.user.login) {
        bisInfo.addTab(tab_rating_title, relleno());
    } else {
        bisInfo.addTab(tab_rating_title, relleno(), function () {
        });
        $(bisInfo.tabs_[1].tab).attr('href', '#user_frm_register').leanModal({closeButton: $("#closerModal")[0]});
        $("#link_learn_more_go_back").leanModal({prevClose: function () {
            $("#lean_overlay").hide();
            $("#learn_more").css({"display": "none"});
            window.location.hash = '';
        }});
        $("#link_lear_more").leanModal({prevClose: function () {
            $("#lean_overlay").hide();
            $("#user_frm_register").css({"display": "none"});
            window.location.hash = '';
        }});
    }
    bisInfo.tabs_[1].tab.removeAttribute('style');
    $(bisInfo.tabs_[1].content).addClass('binfo');
    $(bisInfo.tabs_[1].tab).addClass('tab_info');
    $(bisInfo.tabs_[1].tab).addClass('tab_2');
    $(bisInfo.tabs_[1].tab).click(function () {
        $(bisInfo.tabs_[1].content).find('#tab_video_coupon').hide();
        $(bisInfo.tabs_[0].content).find('#tab_video_pnl01').hide();
    });

    window.onhashchange = function (evt) {
        if (window.location.hash != "") {
            var a = searchUrl(window.location.hash.substr(3, window.location.hash.length));
            $(a.marker.content).trigger('click');
        }
    };

    function relleno() {
        var ps = document.createElement('div');
        ps.innerHTML = "<h2>Relleno</h2>";
        return ps;
    }

    function buildInfoSubFooter(business) {
        $("div#schedule").html("");
        $.getJSON('/communities/get/schedule', {'tag': business.auth_code}, function (data) {
            $("div#schedule").html(data.schedule);
        });
        $("#menuPanelSubFooter div#textMenu").html("");
        $.getJSON('/communities/get/menu', {'tag': business.auth_code}, function (data) {
            $("#menuPanelSubFooter div#textMenu").html(data.menu);
        });
        var listLiMenu = $("#menuPanelSubFooter div#textMenu ul li");
        for (var i = 0; i < listLiMenu.length; i++){
            $(listLiMenu[i]).append("<div class='icon-view'><i><img src='/static/community/evolution/icon-view-menu.png'/></i></div>");
        }
        var panelsFooter = $(".panelBusiness");
        panelsFooter.hide();
        var subFooter = $("#subFooter");
        $.getJSON('/communities/get/session', function (data) {
            if(data.session){
                subFooter.find("#dealsPanelSubFooter #ten-off input#nameBusinessField").val(data.names);
                subFooter.find("#dealsPanelSubFooter #ten-off input#emailBusinessField").val(data.email);
                subFooter.find("#dealsPanelSubFooter #smart-buys input#nameUserField").val(data.names);
                subFooter.find("#dealsPanelSubFooter #smart-buys input#emailUserField").val(data.email)
            }
        });
        subFooter.find("#nameSubFooter").html(business.name);
        subFooter.find("#addressSubFooter").html(business.address);
        subFooter.find("#descSubFooter").html(business.desc);
        subFooter.find("#contactSubFooter #phoneBusiness div").html(business.phones);
        subFooter.find("#contactSubFooter #websiteBusiness a").html(business.site);
        subFooter.find("#contactSubFooter #websiteBusiness a").attr("href", business.site);
        subFooter.find("#reviewSubFooter").attr("getreview", business.url);
        subFooter.find("#menuSubFooter").attr("getmenu", business.url);
        subFooter.find("#infoSubFooter").attr("getschedule", business.url);
        subFooter.find("#servicesSubFooter ul").html(" ");
        subFooter.find("#infoPanelSubFooter").show();
        subFooter.find("#hiddenBusiness").val(business.url);
        $(".thirty, .fourty, .fifty").removeClass("cur").find("span.min").hide();
        $(".dealBehind").remove();
        //subFooter.find("#dealsPanelSubFooter").append("<div class='dealBehind'></div>");
        subFooter.find("#hiddenBusiness").attr("nameBiz", business.name);
        if(business.deals !== 'N'){
            $("#" + business.deals + "deal").addClass("cur").find("span.min").show();
            subFooter.find("#ten-off form.formDeals").show();
            subFooter.find("#ten-off ul#list-share").show();
            subFooter.find("#ten-off .nodeal").hide();
            if(business.deals === 'T'){
                $("section.rounded").css("background","#FCEE21").show();
            }
            if(business.deals === 'F'){
                $("section.rounded").css("background","#FF0000").show();
            }
            if(business.deals === 'Q'){
                $("section.rounded").css("background","#0071BC").show();
            }
        }
        else{
            $(".thirty, .fourty, .fifty").removeClass("cur").find("span.min").hide();
            subFooter.find("#ten-off form.formDeals").hide();
            subFooter.find("#ten-off ul#list-share").hide();
            subFooter.find("#ten-off .nodeal").show();
            subFooter.find("#ten-off .wrapnodeal a.launchdeal").html("<div class='admiral'>!</div><div class='linesplit'></div><div class='namelaunchdeal'><b>" + business.name + "IS NOT ACCEPTING </b><br>$10 SAVINGS CARD AT THIS TIME</div>");
            $("#request_deal h3.requestH3").html("There’s Orange Deals available for " + business.name);
            $("section.rounded").css("background","#B3B3B3").show();
        }
        $("#subFooter").slideDown('slow', function () {
            $.getJSON('/communities/get/schedule', {'tag': business.auth_code}, function (data) {
                $("div#schedule").html(data.schedule);
            });
            $("#menuPanelSubFooter div#textMenu").html("");
            $.getJSON('/communities/get/menu', {'tag': business.auth_code}, function (data) {
                $("#menuPanelSubFooter div#textMenu").html(data.menu);
            });
            $('#left_bar .cat-title').html('');
            $('#left_bar .cat-content').html('');
        });
        subFooter.find("#reviewPanelSubFooter h3").html("Reviews of " + business.name + "<span></span>");
        subFooter.find("#directionPanelSubFooter input.from").attr("placeholder", business.name);
        subFooter.find("#directionPanelSubFooter input#realTo").val(business.address);
        subFooter.find("#dealsPanelSubFooter #ten-off h3").html("Want to save $10 at " + business.name + "?");
        subFooter.find("#dealsPanelSubFooter #smart-buys h3").html("Smart Buys at " + business.name);
        if(!business.ten_visit){
            subFooter.find("#ten-visits .panel-right img").attr("src", "/static/community/evolution/ten-visits-image.png");
        }else{
            subFooter.find("#ten-visits .panel-right img").attr("src", "/media/" + business.ten_visit);
        }
        subFooter.find("#menuPanelSubFooter h3").html(business.name + "'s Menu");
        $("#tweetShare").attr("href", "https://twitter.com/share?url=" + "http%3A%2F%2Fdetourmaps.com%2Fcommunities%2F" + business.community + "%2Fmap%2Fbusiness%2F?name=" + business.url_name + "%26auth_code=" + business.auth_code + "&via=detourmaps")
        $("#faceShare").attr("href", "http://detourmaps.com/communities/" + business.community + "/map/business/?name=" + business.url_name + "&auth_code=" + business.auth_code);
        $("#faceShare").attr("name", business.name);
        $("#faceShare").attr("caption", business.name);
        $("#faceShare").attr("description", business.desc);
        $("#plusShare").attr("href", "https://plus.google.com/share?url=" + "http%3A%2F%2Fdetourmaps.com%2Fcommunities%2F" + business.community + "%2Fmap%2Fbusiness%2F?name=" + business.url_name + "%26auth_code=" + business.auth_code)
        $("#rssShareIt").attr("href", business.url);
        $("#emailShareIt").attr("href", business.url);
        $("#hideBizEvents").val(business.url);
        $("#codeBiz").val(business.url);
        $("#hiddenCoupon").val(business.auth_code);
        $("#bizAuth").val(business.auth_code);
        $("#faceCoupon").attr("name", business.name).attr("caption", business.desc).attr("description", business.description);
        $("#faceMenu").attr("href", business.auth_code);
        $("#tweetMenu").attr("href", business.auth_code);
        if (business.video) {
            $("#ytVideo").attr("src", "http://www.youtube.com/embed/" + business.video + "?wmode=transparent");
            $("#videoInfoView").find("h3").html(business.video_title);
            $("#videoInfoView").find("p").html(business.video_description);
            $("#thumbnailV1").attr("src", business.video_img_0);
            $("#thumbnailV2").attr("src", business.video_img_1);
            $("#thumbnailV3").attr("src", business.video_img_2);
        }
        else {
            $("#ytVideo").attr("src", "");
            $("#thumbnailV1").attr("src", "");
            $("#thumbnailV2").attr("src", "");
            $("#thumbnailV3").attr("src", "");
            $("#videoInfoView").find("h3").html(business.name);
            $("#videoInfoView").find("p").html("");
        }
        if (business.cupon.length > 0) {
            $("#wrap-vertical-slider").html("");
            $(".controlpanel").remove();
            var panel_smart = "";
            var init_page = 1;
            var end_page = Math.round(business.cupon.length/2);
            for(var cup = 0; cup < business.cupon.length; cup++){
                var label = "<label class='namesmart'>" + business.cupon[cup].name + "</label>";
                var idcheck = "<label><input type='checkbox' name='cup" + business.cupon[cup].id + "' value='" + business.cupon[cup].id + "'/>SELECT SMART BUY</label>";
                var linksave = "<a href='' idb='cup" + business.cupon[cup].id + "'>SAVE TO MY DEALS</a>";
                var no_purchase = "<p>No purchased required</p>";
                var valid_through = "<p>Valid through " + business.cupon[cup].start_date + "-" + business.cupon[cup].end_date + "</p>";
                var img = "<a class='couponPop' href='/media/" + business.cupon[cup].medium + "'><img src='/media/" + business.cupon[cup].small + "'/></a>"
                var div_left = "<div class='lsmart'>" + label + no_purchase + valid_through + "<div class='toolset'>" + idcheck + linksave + "</div></div>";
                var div_right = "<div class='rsmart'><figure>" + img + "</figure></div>";
                panel_smart += "<div class='panel_smart'>" + div_left + div_right + "</div>";
            }
            $("#wrap-vertical-slider").html(panel_smart);
            var divpager = "";
            var uparrow = "<a href='' class='fup'><img src='/static/community/evolution/icon-up-bubble.png'/></a>";
            var downarrow = "<a href='' class='fdown'><img src='/static/community/evolution/icon-down-bubble.png'/></a>";
            var stepcontrol = "<label><span class='dynamo'>" + init_page + "</span> of " + end_page + "</label>";
            divpager = "<div id='controlpanel'>" + uparrow + stepcontrol + downarrow + "</div>";
            $("#vertical-slider").append(divpager);
            subFooter.find("#smart-buys #smartDeals button#printCoupon").css("display", "inline-block");
            subFooter.find("#smart-buys #smartDeals div.splinter").css("display", "inline-block");
            subFooter.find("#smart-buys #smartDeals button#emailCoupon").css("display", "inline-block");
        }
        else {
            $("#wrap-vertical-slider").html("");
            subFooter.find("#smart-buys #smartDeals button#printCoupon").css("display", "none");
            subFooter.find("#smart-buys #smartDeals div.splinter").css("display", "none");
            subFooter.find("#smart-buys #smartDeals button#emailCoupon").css("display", "none");
        }
        var node = "";
        for (var iTag = 0; iTag < business.tags.length; iTag++) {
            var tag = cmData.tags[business.tags[iTag]];
            node = '<li><div class="imgTag"><img src="" style="background:url(/media/' + tag.icon + ')"/></div><div class="textTag">' + tag.name + '</div></li>'
            subFooter.find('#servicesSubFooter ul').append(node);
        }
        var b_left = $('#left_bar');
        b_left.css('height', $('#detourmap').css('height'));
        b_left.css('bottom', '');
        var _d = b_left.parent().height() - 65;
        b_left.animate({height: '-=' + _d}, 500, function () {
            b_left.addClass('float_map');
        });
        b_left.attr('show', 'false');

    }
    function translape(index, lista, _this){
        $("#wrapper-slide-deals").css("transform","translateX("+index * -25+"%)");
        $("a.barNavDeals").not(_this.find("a")).removeClass('active');
        _this.find("a").addClass('active');
        for(var x=0; x<lista.length; x++){
            $(lista[x]).find("img").attr("src", $(lista[x]).attr("inactive"));
        }
        var active = _this.find("a").attr("active");
        _this.find("a").find("img").attr("src", active);
        var tabNameDeals = _this.find("a").attr("name");
        var uri = updateQueryStringParameter(location.href, "tab", "deals|" + tabNameDeals);
        changeLocation(uri);
    }
    function showPanels(_this){
        $("div.activeNav").not(_this.next()).hide();
        var tabName = _this.attr("name");
        var uri = updateQueryStringParameter(location.href, "tab", tabName);
        changeLocation(uri);
        _this.next().show();
        var reference = _this.attr("href");
        $(".panelBusiness").not($(reference)).hide();
        $(reference).show();
    }
    function buildInfoBubble(latlong, m) {
        try {
            detourmaps.eventBubble.close();
        } catch (e) {
        }
        var b = m || this;
        var cat = cmData.cat[b.ci];
        var bis = cat.bis[b.bi];
        if(directionsDisplay != null){
            directionsDisplay.setMap(null);
            directionsDisplay = null;
        }
        buildInfoSubFooter(bis);

        document.title = bis.name + ' - DetourMaps';
        $("meta[name='Description']").attr("content", bis.desc);
        try {
            bisInfo.close();
        } catch (e) {
        }

        $.getJSON("/communities/business/review", {'bis': bis.id}, function (data) {
            cmData.cat[b.ci].bis[b.bi]['comments'] = data;
            if ((ci != b.ci || bi != b.bi)) {
                $('.rbar .overmap').remove();
                ci = b.ci; //This assignment is because events are not always inside or sync
                bi = b.bi;
                bb = $($('#templates .binfo').clone()[0]);
                bb.find('h3').html(bis.name + "<span>" + cmData.cat[b.ci].name + "</span>");
                bb.find("a.show-more").css("color", "red").click(function(event){
                    event.preventDefault();
                    $("html, body").animate({
                        scrollTop: 350
                    }, 400);
                });
                //bb.find('span.address').html(bis.address);
                //bb.find('span a.from').attr('href', 'http://maps.google.com/maps?saddr=' + bis.address.replace(/\s/g, '+'));
                //bb.find('span a.to').attr('href', 'http://maps.google.com/maps?daddr=' + bis.address.replace(/\s/g, '+'));
                //bb.find('span.phone').html(bis.phones);
                //bb.find('span.partner').html(bis.partner)
                if (bis.subscription) {
                    bb.find('p.des').html("<b>What's Popular</b><br/>" + bis.desc);
                    //bb.find('span.url a').html(bis.site.slice(7).split('/')[0]).attr('href', bis.site);
                    if (bis.tt.length > 4) {
                        bb.find('span.tt a').attr('href', bis.tt);
                    } else {
                        bb.find('span.tt').remove();
                    }
                    if (bis.fb.length > 4) {
                        bb.find('span.fb a').attr('href', bis.fb);
                    } else {
                        bb.find('span.fb').remove();
                    }
                    bb.find('button.reviews').click(function () {
                        $('.rbar div.stars').fadeOut(333);
                        $('.rbar span.soon').animate({opacity: 1}, 333);
                        $(this).animate({right: 108}, 333);
                    });
                    for (var i = 0; i < bis.img.length; i++) {
                        var gallery = bb.find('div.lpanel div.img-wrap');
                        var image = bis.img[i].img.replace("\\", "/");
                        gallery.append('<img src="/media/' + image + '" alt="' + bis.img[i].name + '" class="imgSlider"/>');
                    }
                    var widthWrap = bis.img.length * 215;
                    bb.find('div.img-wrap').css({'width': widthWrap, 'height': '198px'});
                    bb.find("div.lpanel div.img-wrap").slider({
                        width: 215,
                        height: 198,
                        speed: 2000,
                        speedSlide: 333
                    });

                } else {
                    bb.find('div.review-wrap').remove();
                    bb.find('address .social').remove();
                    bb.find('div.tags').remove();
                }

                if (bis.address.trim() == '') {
                    bb.find('span.address').next().remove();
                    bb.find('span.address').remove();
                    bb.find('span.directions').next().remove();
                    bb.find('span.directions').remove();
                    var over = $('#templates .overmap').clone();
                    over.find('.c').click(function () {
                        $('.rbar .overmap').remove();
                    });
                    over.find('.m').append(bb);
                    over.appendTo('.rbar');
                } else {
                    if (map.getZoom() < 14) {
                        map.setZoom(14);
                    }

                    bisInfo.tabs_[0].content = bb[0];
                    bisInfo.open(map, b, function () {
                        urlChanger(null, bis, tab);
                        if(tab.subtab){
                            var currentTab = $("a#"+ tab.tab +"SubFooter");
                            showPanels(currentTab);
                            var currentSubTab = $("li#" + tab.subtab + "-ctrl");
                            translape(currentSubTab.index(), $("a.barNavDeals"), currentSubTab);
                        }
                        else{
                            var currentTab = $("a#"+ tab.tab +"SubFooter");
                            showPanels(currentTab);
                        }
                    });
                    bisInfo.setTabActive(1);
                    bisInfo.removeTab(1);
                }
                if (bis.phones.trim() == '') {
                    bb.find('span.phone').next().remove();
                    bb.find('span.phone').remove();
                }
            } else {
                if (bis.address.trim() == '') {
                    if ($('.rbar .overmap').length == 0) {
                        var over = $('#templates .overmap').clone();
                        over.find('.c').click(function () {
                            $('.rbar .overmap').remove();
                        });
                        over.find('.m').append(bb);
                        over.appendTo('.rbar');
                    }
                } else {
                    bisInfo.open(map, b, function () {
                        urlChanger(null, bis, tab);
                        if(tab.subtab){
                            var currentTab = $("a#"+ tab +"SubFooter");
                            showPanels(currentTab);
                            var currentSubTab = $("li#" + tab.subtab + "-ctrl");
                            translape(currentSubTab.index(), $("a.barNavDeals"), currentSubTab);
                        }
                        else{
                            var currentTab = $("a#"+ tab +"SubFooter");
                            showPanels(currentTab);
                        }
                    });
                    bisInfo.setTabActive(1);
                    bisInfo.removeTab(1);

                }
            }
            $("#greatFooter").animate({marginTop: -150}, 800).animate({marginTop: 0}, 2400);

        });
        window.setTimeout(function () {
            $($('article.binfo')[0]).parent().parent().prev().css({
                overflow: 'hidden',
                'border-radius': '8px'
            });
        }, 500);
    }

    /**
     *
     * @param ci
     * @param bi
     * @param cat
     * @return {*} Marker
     */
    function buildMarker(ci, bi, cat) {
        var title = cmData.cat[ci].bis[bi].name;
        var color = cmData.cat[ci].color;
        var content;
        var incat = cat || $('.cat.selected').length;
        if (cmData.cat[ci].bis[bi].subscription) {
            if (incat) {
                content = $($('.marker.big').clone()[0]);
                content.attr('title', title);
                if ($.browser.msie && parseFloat($.browser.version) < 9) {
                    var paper = Raphael(content[0], 22, 22);
                    var circle1 = paper.circle(11, 11, 10);
                    circle1.attr("fill", "#" + color);
                    circle1.attr("stroke", "#" + color);
                    circle1.attr("stroke-width", 1);
                    circle1.attr("stroke-dasharray", "null");
                    circle1.attr("stroke-linecap", "null");
                    circle1.attr("stroke-linejoin", "null");
                } else {
                    content.find('title').text(title);
                    content.find('circle:nth-child(2)').attr('fill', '#' + color);
                    content.find('circle:nth-child(3)').attr('stroke', '#' + color);
                }
                content.find('div img').attr('src', '/media/' + cmData.cat[ci].img);
            } else {
                content = $($('.marker.small').clone()[0]);
                content.attr("title", title);
                if ($.browser.msie && parseFloat($.browser.version) < 9) {
                    var paper = Raphael(content[0], 16, 16);
                    var circle1 = paper.circle(8, 8, 4);
                    circle1.attr("fill", "#" + color);
                    circle1.attr("stroke", "#" + color);
                    circle1.attr("stroke-width", 1);
                    circle1.attr("stroke-dasharray", "null");
                    circle1.attr("stroke-linecap", "null");
                    circle1.attr("stroke-linejoin", "null");
                    var circle2 = paper.circle(8, 8, 7);
                    circle2.attr("fill", "none");
                    circle2.attr("stroke", "#" + color);
                    circle2.attr("stroke-dasharray", "2,2");
                    circle2.attr("stroke-width", 2);
                } else {
                    content.find('title').text(title);
                    content.find('circle:nth-child(2)').attr('stroke', '#' + color);
                    content.find('circle:nth-child(3)').attr('fill', '#' + color);
                }
            }
        } else {
            content = $($('.marker.smaller').clone()[0]);
            content.attr("title", title);
            if ($.browser.msie && parseFloat($.browser.version) < 9) {
                var paper = Raphael(content[0], 10, 10);
                var circle = paper.circle(5, 5, 4);
                circle.attr("fill", "#" + color);
                circle.attr("stroke", "#" + color);
                circle.attr("stroke-width", 1);
                circle.attr("stroke-dasharray", "null");
                circle.attr("stroke-linecap", "null");
                circle.attr("stroke-linejoin", "null");
            } else {
                content.find('title').text(title);
                content.find('circle:nth-child(2)').attr('fill', '#' + color);
            }
        }
        content = content[0];
        var marker;
        if (cmData.cat[ci].bis[bi].marker && cmData.cat[ci].bis[bi].address != '') {
            marker = cmData.cat[ci].bis[bi].marker;
            marker.setMap(map);
            marker.setContent(content);
        } else {
            var geo = cmData.cat[ci].bis[bi].geo || undefined;
            var r = geo.slice(7, geo.length - 1).split(' ') || [];

            var latlng = new google.maps.LatLng(parseFloat(r[1]), parseFloat(r[0]));
            marker = new RichMarker({
                position: latlng,
                map: map,
                title: title,
                content: content,
                flat: true,
                ci: ci,
                bi: bi
            });
            /**
             * TODO faltan agregar los listener en los controles que seleccionan las comunidades
             */
            google.maps.event.addListener(map, 'click', function () {
                bisInfo.close();
            });
            google.maps.event.addListener(marker, 'click', buildInfoBubble);
            google.maps.event.addListener(marker, 'mouseover', function () {
                notOverMarker = false;
            });
            google.maps.event.addListener(marker, 'mouseout', function () {
                notOverMarker = true;
            });
            cmData.cat[ci].bis[bi].marker = marker;
            if (cmData.cat[ci].bis[bi].address == '') {
                marker.setMap(null);
            }
        }
        if (incat && cmData.cat[ci].bis[bi].subscription) {
            marker.setAnchor(new google.maps.Size(-11, -11));
        } else if (!incat && cmData.cat[ci].bis[bi].subscription) {
            marker.setAnchor(new google.maps.Size(-8, -8));
        } else {
            marker.setAnchor(new google.maps.Size(-5, -5));
        }
        return marker;
    }

    function clearMarkers() {
        for (var j = 0; j < cmData.cat.length; j++) {
            for (var k = 0; k < cmData.cat[j].bis.length; k++) {
                if (cmData.cat[j].bis[k].marker) {
                    cmData.cat[j].bis[k].marker.setMap(null);
                }
            }
        }
    }

    function renderMarkers() {
        clearMarkers();
        if ($('.cat.selected').length > 0) {
            var ci = parseInt($('.cat.selected').attr('id').slice(4));
            for (var bi = 0; bi < cmData.cat[ci].bis.length; bi++) {
                buildMarker(ci, bi);
            }
        } else {
            for (var ci = 0; ci < cmData.cat.length; ci++) {
                for (var bi = 0; bi < cmData.cat[ci].bis.length; bi++) {
                    if (cmData.cat[ci].bis[bi].subscription) {
                        buildMarker(ci, bi);
                    }
                }
            }
        }
    }

    function getURLParameter(name) {
        return decodeURI(
            (RegExp(name + '=' + '(.+?)(&|$)').exec(location.search) || [, null])[1]
        );
    }

    function urlBusiness() {
        var name = getURLParameter("name");
        var auth_code = getURLParameter("auth_code");
        var decodeURL = decodeURIComponent(auth_code);
        var urlName = name + "/" + decodeURL;
        var result = searchUrl(urlName);
        if (result) {
            buildMarker(result.ci, result.bi, "");
            buildInfoBubble(null, result.biz.marker);
        }
    }

    var renderTryCount = 0;

    function dataAvailable() {
        if (cmData) {
            //Mapa
            var bounds = new google.maps.LatLngBounds();
            var latlng;
            if (!$.isPlainObject(cmData.community.border)) {
                cmData.community.border = $.parseJSON(cmData.community.border);
            }
            var commCoords = [];
            var coords = cmData.community.border.coordinates;
            for (var n = 0; n < coords[0][0].length; n++) {
                latlng = new google.maps.LatLng(coords[0][0][n][1], coords[0][0][n][0]);
                commCoords.push(latlng);
                bounds.extend(latlng);
            }
            map = new google.maps.Map(document.getElementById("map"), {
                zoom: 13,
                center: latlng,
                disableDefaultUI: false,
                navigationControl: true,
                scrollwheel: false,
                scaleControl: true,
                zoomControl: true,
                zoomControlOptions: {
                    style: google.maps.ZoomControlStyle.SMALL
                },
                navigationControlOptions: {
                    style: google.maps.NavigationControlStyle.SMALL,
                    position: google.maps.ControlPosition.RIGHT_CENTER
                },
                mapTypeControl: true,
                mapTypeControlOptions: {
                    style: google.maps.MapTypeControlStyle.DROPDOWN_MENU,
                    position: google.maps.ControlPosition.RIGHT_BOTTOM,
                    mapTypeIds: [
                        google.maps.MapTypeId.SATELLITE,
                        google.maps.MapTypeId.HYBRID,
                        google.maps.MapTypeId.TERRAIN,
                        'dtm']
                },
                mapTypeId: 'dtm'
            });
            var dtmMapType = new google.maps.StyledMapType(dtmStyle, {
                map: map,
                name: "Map"
            });
            map.mapTypes.set('dtm', dtmMapType);
            map.setMapTypeId('dtm');
            map.fitBounds(bounds);

            var polygon = new google.maps.Polygon({
                paths: commCoords,
                strokeColor: "#f48131",
                strokeOpacity: 1,
                strokeWeight: 2,
                fillColor: "#FFFFFF",
                fillOpacity: 0
            });
            polygon.setMap(map);
            renderMarkers();
            //Dependent events
            $('#categories .cat').click(function () {
                $("#left_bar").css("overflow", "visible");
                $("#left_bar .cat-content").css("overflow", "visible");
                if ($(this).hasClass('selected')) {
                    $('#left_bar').find('.cat-list').css('top', '0');
                    $(this).removeClass('selected');
                    $('#left_bar .cat-title').html('');
                    $('#left_bar .cat-content').html('');
                    $('#left_bar').addClass('clear');
                } else {
                    if ($('#left_bar').attr('show') == 'false')
                        $('div#left_bar div.show_hide > div:first-child').trigger('click');
                    $('#left_bar').removeClass('clear');
                    $('#categories .cat.selected').removeClass('selected');
                    $(this).addClass('selected');
                    $('#left_bar .cat-title').html($(this).find('.cat-title').clone().html());
                    $('#left_bar .cat-content').html($(this).find('.cat-content').clone().html());

                    //setCatListHeight();
                    var __h = $('div#left_bar').find('div.cat-filter').height() + 15;
                    var __t = $('div#left_bar').find('div.cat-title').height();
                    var __lb = $("div#left_bar").height();
                    var realAltoSearchResult = $("div#map").height() - ($("div.cat-filter").height() + $("div.cat-title").height());
                    $("div.cat-list").css({
                        "height": realAltoSearchResult
                    });
                }
                renderMarkers();
                if (typeof window.history.pushState == 'function') {
                    window.history.replaceState({}, 'Root', window.location.pathname);
                } else {
                    window.location.hash = "";
                }
                //  events
                $('#left_bar .tags .tag').click(function () {
                    $(this).toggleClass('active');
                    var activeServices = [];
                    $('#left_bar .tags .tag.active').each(function (i, node) {
                        activeServices.push($(node).attr('for').slice(3));
                    });
                    $('#left_bar .cat-list li').each(function (i, node) {
                        var ci = parseInt($('.cat.selected').attr('id').slice(4));
                        var bi = parseInt($(node).attr('bindex'));
                        var tags = cmData.cat[ci].bis[bi].tags;
                        var count = 0;
                        for (var r = 0; r < activeServices.length; r++) {
                            var found = false;
                            for (var s = 0; s < tags.length; s++) {
                                if (activeServices[r] == tags[s]) {
                                    found = true;
                                    count++;
                                    break;
                                }
                            }
                            if (!found) {
                                break;
                            }
                        }
                        if (count == activeServices.length) {
                            $(node).removeClass('hide');
                            buildMarker(ci, bi);
                        } else {
                            $(node).addClass('hide');
                            cmData.cat[ci].bis[bi].marker.setMap(null);
                        }
                    });
                    return false;
                });
                $('#left_bar .tags .tag').mouseenter(function () {
                    var activeService = $(this).attr('for').slice(3);
                    var ci = parseInt($('.cat.selected').attr('id').slice(4));
                    $('#left_bar .cat-list li').each(function (i, node) {
                        var bi = parseInt($(node).attr('bindex'));
                        var tags = cmData.cat[ci].bis[bi].tags;
                        var found = false;
                        for (var s = 0; s < tags.length; s++) {
                            if (activeService == tags[s]) {
                                found = true;
                                break;
                            }
                        }
                        if (found) {
                            $(node).addClass('match-over');
                        } else {
                            $(node).removeClass('match-over');
                        }
                    });
                    return false;
                });
                $('#left_bar .tags').mouseleave(function () {
                    $('#left_bar .cat-list li.match-over').removeClass('match-over');
                });
                $('#left_bar .cat-list li').click(function (event) {
                    var bi = parseInt($(this).attr('bindex'));
                    var ci = parseInt($('.cat.selected').attr('id').slice(4));
                    buildInfoBubble(null, cmData.cat[ci].bis[bi].marker);
                    return false;
                });
            });
            urlBusiness();
            bounds = new google.maps.LatLngBounds();
            var polygons = [];
            var markers = [];
            for (var j = 0; j < communities.length; j++) {
                if (communities[j].name != curCommunity) {
                    var pcoords = [];
                    var tmpBounds = new google.maps.LatLngBounds();
                    for (var k = 0; k < communities[j].geojson.coordinates[0][0].length; k++) {
                        var coord = communities[j].geojson.coordinates[0][0][k];
                        var latlng = new google.maps.LatLng(coord[1], coord[0]);
                        pcoords.push(latlng);
                        bounds.extend(latlng);
                        tmpBounds.extend(latlng);
                    }
                    polygons.push(new google.maps.Polygon({
                        paths: pcoords,
                        strokeColor: "#f48131",
                        strokeOpacity: 1,
                        strokeWeight: 2,
                        fillColor: "#f48131",
                        fillOpacity: 0.1,
                        url: communities[j].url_name,
                        map: map
                    }));
                    latlng = tmpBounds.getCenter();
                    markers.push(new RichMarker({
                        position: latlng,
                        title: communities[j].name,
                        content: '<h3 class="cmm-title">' + communities[j].name + '</h3>',
                        flat: true,
                        url: communities[j].url_name,
                        map: map
                    }));
                }
            }
            for (var n = 0; n < polygons.length; n++) {
                polygons[n].setMap(map);
                markers[n].setMap(map);
                google.maps.event.addListener(polygons[n], 'click', function () {
                    if (notOverMarker) {
                        window.location.href = mapConstructorURL.replace('replace', this.url);
                    }
                });
                google.maps.event.addListener(polygons[n], 'mouseover', function () {
                    this.setOptions({
                        fillColor: "#ffffff",
                        fillOpacity: 0.5
                    });
                });
                google.maps.event.addListener(polygons[n], 'mouseout', function () {
                    this.setOptions({
                        fillColor: "#f48131",
                        fillOpacity: 0.1
                    });
                });
            }
            if (lhash != undefined) {
                setTimeout(function () {
                    var bus;
                    if (lhash.split('/')[1] != 'event') {
                        bus = searchUrl(lhash.substr(3, lhash.length));
                        $(bus.marker.content).trigger('click');
                    } else {
                        bus = searchEventURL(lhash.substr(3, lhash.length));
                        buildEventBubble(bus);
                    }

                }, 1000);
            }

        } else {
            if (renderTryCount > 0 && renderTryCount % 50 == 0) {
                $('#detourmap div.messages').append('<span>' + msgs[renderTryCount / 50] + '</span>');
            } else if (renderTryCount > 550) {
                $('#detourmap div.messages').append('<span>Sorry...</span>');
            }
            renderTryCount++;
            window.setTimeout(dataAvailable, 33);
        }
    }

    var msgs = ['', 'Seems like that...', 'sometimes...', 'like this!', 'Try reloading the page!'];
    dataAvailable();
    //window.setTimeout(urlBusiness,5000);
    $('#categories .cat').click(function () {
        if (!cmData) {
            new Messi("Wait please ..  building map!!!", {title: 'DetourMaps - Alert System', modal: true});
        }
    });

    // TopBar Nav Hover & Menus!


    //            //            //

    function setCatListHeight() {
        var height = $('.lbar,#left_bar').height();
        height -= $('.lbar div.search,#left_bar div.search').height() + 8;
        height -= $('.lbar div.cat-title,#left_bar  div.cat-title').height() + 16;
        $("#left_bar").css("overflow", "visible");
        $("#left_bar").find(".cat-content").css(
            {
                "overflow": "visible",
                "top": 0
            }
        );
        $("#left_bar .cat-content").find(".cat-list").css("top", "98");
        if ($('.lbar div.cat-filter,#left_bar div.cat-filter').length) {
            height -= $('.lbar div.cat-filter,#left_bar div.cat-filter').height() + 18;
        }
        //$('.lbar div.cat-list, #left_bar div.cat-list').height(height);
        return height;
    }

    $(window).resize(function () {
        //setCatListHeight();
    });
    // Search
    function searchBusiness(text) {
        var terms = text.split(/\s/);
        var results = [];
        terms = terms.map(function (t) {
            return new RegExp(t, 'i');
        });
        for (var p = 0; p < cmData.cat.length; p++) {
            for (var q = 0; q < cmData.cat[p].bis.length; q++) {
                var bis = cmData.cat[p].bis[q];
                var match = true;
                /*
                 for (var i = 0; i < terms.length; i++) {
                 if (bis.name.search(terms[i]) == -1) {
                 match = false;
                 break;
                 }
                 }
                 if (match) {
                 bis.ci = p;
                 bis.bi = q;
                 results.push(bis);
                 }*/
                var texto = cmData.cat[p].bis[q].name.toLowerCase();
                if (texto.indexOf(text.toLowerCase()) != -1) {
                    var bis = cmData.cat[p].bis[q];
                    bis.ci = p;
                    bis.bi = q;
                    results.push(bis);
                }
            }
        }
        return results;
    }


    function renderSearchResults(results) {
        clearMarkers();
        var cnt = $('<div class="cat-list"><ul></ul></div>');
        $('.lbar .cat-title, #left_bar .cat-title').html('<div><span class="title">Search Results</span></div>');
        $('.cat-title').show();
        for (var i = 0; i < results.length; i++) {
            buildMarker(results[i].ci, results[i].bi, true);
            cnt.find('ul').append($('<li></li>').text(results[i].name).attr({
                cindex: results[i].ci,
                bindex: results[i].bi
            }));
        }
        cnt.find('li').click(function () {
            var ci = parseInt($(this).attr('cindex'));
            var bi = parseInt($(this).attr('bindex'));
            buildInfoBubble(null, cmData.cat[ci].bis[bi].marker);
            return false;
        });
        $('.lbar .cat-content,#left_bar .cat-content').html(cnt);
        $("#left_bar .cat-list").css("top", 98);
        var __t = $('div#left_bar').find('div.cat-title').innerHeight();
        var __lb = $("div#left_bar").height();
        var heightFooter = $("#map").height();
        var realHeight = heightFooter - $('div.cat-title').innerHeight();
        $('#left_bar').find('.cat-list').css('height', realHeight);
        if ($('#left_bar').attr('show') == 'false')
            $('div#left_bar div.show_hide > div:first-child').trigger('click');
        setCatListHeight();
    }

    var text = '';
    var timedSearch = false;

    function searchHandler(e) {
        $("#left_bar").css("overflow", "visible");
        var val = $('.search input').prop('value').trim();
        if (text != val && val != '') {
            text = val;
            $('#categories .cat.selected').click();
            renderSearchResults(searchBusiness(text));
        } else if (text != val && val == '' && $('#categories .cat.selected').length == 0) {
            text = val;
            $('.lbar .cat-title,#left_bar .cat-title').html('');
            $('.lbar .cat-content,#left_bar .cat-content').html('');
            renderMarkers();
        }
    }

    $('.lbar .search input,#left_bar .search input').focus(function () {
        $('.lbar .search .search-icon,#left_bar .search .search-icon').addClass('focus');
    }).blur(function () {
            $('.lbar .search .search-icon, #left_bar .search .search-icon').removeClass('focus');
        });
    $('.lbar .search input,#left_bar .search input').change(searchHandler).keyup(searchHandler).click(searchHandler);
    $('#categories>ul>li').bind('click', function () {
        $('.lbar .search input,#left_bar .search input').val('');
        $('.lbar, #left_bar').addClass('clear');
        $('.lbar .cat-title,#left_bar .cat-title').html('');
        $('.lbar .cat-content,#left_bar .cat-content').html('');
        $('#left_bar .left_bar_body').css('display', 'block');
    });
});

/**
 * Retorna un objeto con los datos del Negocio.
 * @param url
 * @return {*}
 */
function searchUrl(url) {
    for (var p = 0; p < cmData.cat.length; p++) {
        for (var q = 0; q < cmData.cat[p].bis.length; q++) {
            bis = cmData.cat[p].bis[q];
            if (url == bis.url) {
                return {'biz': bis, 'ci': p, 'bi': q};
            }
        }
    }
    return null;
}

function cleanList(obj) {
    while (obj.hasChildNodes()) {
        obj.removeChild(obj.lastChild);
    }
}

function RattingCnt(obj) {
    var self = this;
    this.value = 0;
    this.container = document.createElement('div');
    this.starLength = 5;
    this.comment = '';
    this.isSaving = varDetourmaps.user.login;
    this.service = '/communities/data/ratebusiness';
    this.bdata = arguments[0]['bdata'] || {};
    this.success = function (data) {
    };
    this.isActive = true;

    this.proccesLayer = document.createElement('div');
    this.proccesLayer.setAttribute('class', 'loader');
    var img_prog = document.createElement('img');
    img_prog.setAttribute('src', '/static/community/img/icons/loader.gif');
    this.proccesLayer.appendChild(img_prog);

    this.stars_continer = new Array();
    this.stars = new Array();
    this.startClick = function () {
    };
    for (var prop in obj) {
        for (var _prop in this) {
            if (_prop == prop) {
                this[_prop] = obj[prop];
            }
        }
    }

    var __w = 14;
    for (var x = 0; x < this.starLength; x++) {
        this.stars_continer[x] = document.createElement('div');
        this.stars_continer[x].setAttribute('style', 'border:none;position: absolute;top:0px;left:' + __w + 'px;width:20px; height: 20px;');
        __w += 22;

        this.stars[x] = document.createElement('span');
        if (x < this.value) {
            this.stars[x].setAttribute('class', 'j_star_off j_star_on');
        } else {
            this.stars[x].setAttribute('class', 'j_star_off');
        }
        if (self.isSaving) {
            this.stars[x].setAttribute('style', 'cursor: pointer;');
            this.stars[x].onmouseover = function (event) {
                var cnt = this.parentNode.parentNode;
                for (var x = 0; x < cnt.children.length; x++) {
                    cnt.childNodes[x].childNodes[0].setAttribute('class', 'j_star_off');
                }
                for (var j = 0; j <= $(this.parentNode).index(); j++) {
                    $(this.parentNode.parentNode.childNodes[j].childNodes[0]).addClass('j_star_on');
                }
            };
            this.stars[x].onmouseout = function (event) {
                var cnt = this.parentNode.parentNode;
                for (var x = 0; x < cnt.children.length; x++) {
                    cnt.childNodes[x].childNodes[0].setAttribute('class', 'j_star_off');
                }
                for (var j = 0; j < self.value; j++) {
                    $(cnt.childNodes[j].childNodes[0]).addClass('j_star_on');
                }
            };
            this.stars[x].onclick = function (event) {
                this['index'] = $(this.parentNode).index();
                self.value = this['index'] + 1;
                //self.toProcces(true);
                //self.save(self.success,$(this.parentNode).index() + 1);
            };
        }

        this.stars_continer[x].appendChild(this.stars[x]);
        this.container.appendChild(this.stars_continer[x]);
    }
    this.container.setAttribute('style', 'position: relative;' +
        'width:' + (30 + (22 * this.starLength)) + 'px; height: 22px; ' +
        'text-align: center;border-radius: 12px;' +
        'moz-border-radius: 12px;-webkit-border-radius: 12px;' +
        'box-shadow: inset 0 0 8px rgba(0,0,0,0.4);' +
        'margin-left: auto;margin-right: auto;');
}
RattingCnt.prototype.toProcces = function (active) {
    //<div class="loader"><img src="/static/community/img/icons/loader.gif"></div>
    if (this.value == 0) {
        return false;
    }
    if (active) {
        this.container.appendChild(this.proccesLayer);
    } else {
        this.container.removeChild(this.proccesLayer);
    }
    return true;
};
RattingCnt.prototype.save = function () {
    if (varDetourmaps.user.login) {
        var self = this;
        if (!this.toProcces(true)) {
            alert("Set some rating for this business.");
            return false;
        }
        var _ci = this.bdata.ci;
        var _bi = this.bdata.bi;
        $.ajax({
            type: 'POST',
            url: this.service,
            i: {bi: _bi, ci: _ci},
            data: {
                bis: cmData.cat[_ci].bis[_bi].id,
                stars: parseInt(self.value),
                comment: self.comment
            },
            success: function (data) {
                self.success(data);
                self.value = parseInt(data.stars);
                self.toInactive(true);
                self.toProcces(false);
                show_hide_comments(true);
                cmData.cat[_ci].bis[_bi]['comments'] = [data].concat(cmData.cat[_ci].bis[_bi]['comments'] || []);
                $((new CommentMaker({
                    id: data.id || undefined,
                    username: data.username,
                    stars: data.stars,
                    comment: data.comment
                })).container).appendTo("#comment_list");
            },
            error: function (data, text, srvText) {
                alert("You can't rate this business until 30 days after the last time.");
                self.toInactive(true);
                self.toProcces(false);
            }
        });
    } else {
        alert('You must login!');
    }
};
RattingCnt.prototype.toInactive = function (active) {
    var self = this;
    if (active) {
        //para desactivar el control
        for (var x = 0; x < this.stars_continer.length; x++) {
            this.stars[x].setAttribute('class', 'j_star_off');

            this.stars[x].onmouseover = null;
            this.stars[x].onmouseout = null;
            this.stars[x].onclick = null;
        }
        this.isActive = false;
    } else {
        this.isActive = true;
        //Para activar el control
        for (var x = 0; x < this.stars_continer.length; x++) {
            this.stars[x].setAttribute('class', 'j_star_off');
            this.stars[x].setAttribute('style', 'cursor: pointer;');

            this.stars[x].onmouseover = function (event) {
                for (var j = 0; j <= $(this.parentNode).index(); j++) {
                    $(this.parentNode.parentNode.childNodes[j].childNodes[0]).addClass('j_star_on');
                }
            };
            this.stars[x].onmouseout = function (event) {
                var cnt = this.parentNode.parentNode;
                for (var x = 0; x < cnt.children.length; x++) {
                    cnt.childNodes[x].childNodes[0].setAttribute('class', 'j_star_off');
                }
            };
            this.stars[x].onclick = function (event) {
                self.value = $(this.parentNode).index() + 1;
                this['index'] = $(this.parentNode).index();
                self.toProcces(true);
                self.save();
            };
        }
    }
};

function StarsViewer() {
    this.value = parseInt(arguments[0]['value']) || 0;
    this.length = parseInt(arguments[0]['length']) || 5;
    this.setValue = function () {
    };

    this.container = document.createElement('div');
    this.container.style['display'] = 'inline-block';
    for (var i = 0; i < this.length; i++) {
        var star = document.createElement('div');
        star.style['width'] = '20px';
        star.style['height'] = '20px';
        star.style['display'] = 'inline-block';
        if (i < this.value) {
            star.className = 'j_star_on';
        } else {
            star.className = 'j_star_off';
        }
        this.container.appendChild(star);
    }
}

function CommentMaker() {
    var _self = this;
    this.id = arguments[0]['id'] || undefined;
    this.username = (arguments[0]['username']).split('@')[0] || undefined;
    this.comment = arguments[0]['comment'] || undefined;
    this.stars = parseInt(arguments[0]['stars']) || 0;
    this.date = arguments[0]['date'] || undefined;

    this.container = document.createElement('table');
    this.container.className = 'comment';
    this.container.style['width'] = '100%';
    this.business_id = parseInt(arguments[0]['business_id']) || undefined;

    var row1 = document.createElement('tr');
    var row1_cell1 = document.createElement('td');
    row1_cell1.style['width'] = '110px';
    row1_cell1.appendChild((new StarsViewer({value: this.stars})).container);
    var row1_cell2 = document.createElement('td');
    row1_cell2.textContent = 'by: ' + this.username;
    row1.appendChild(row1_cell1);
    row1.appendChild(row1_cell2);

    this.container.appendChild(row1);
    if (this.comment != undefined) {
        var row2 = document.createElement('tr');
        var row2_cell1 = document.createElement('td');
        row2_cell1.setAttribute('colspan', '2');
        row2_cell1.textContent = this.comment;
        row2.appendChild(row2_cell1);

        var row3 = document.createElement('tr');
        var row3_cell1 = document.createElement('td');
        row3_cell1.setAttribute('colspan', '2');
        var link = document.createElement('a');
        link.setAttribute('style', 'float: right;');
        link.setAttribute('href', '#frm_report_comment');
        link.textContent = 'report';
        link.onclick = function (evt) {
            $("#frm_report_comment").find("#__comment_id").val(_self.id);
        };
        $(link).leanModal();
        row3_cell1.appendChild(link);
        row3.appendChild(row3_cell1);

        this.container.appendChild(row2);
        this.container.appendChild(row3);
    }
}

var rattedBusiness = {
    /*
     Diferencia de fechas
     (((((Date.parse('Wed Sep 05 2012') - Date.parse('Wed Sep 04 2012'))/1000)/60)/60)/24)
     */
    getDate: function (obj) {
        var pasador = $.cookie('rattedBusiness');
        var _obj = JSON.parse(pasador);
        var date = _obj[obj.cat][obj.bis]['date'];
        return date;
    },

    addRatted: function (obj) {
        var pasador = $.cookie('rattedBusiness');
        var _obj = JSON.parse(pasador);
        _obj.data.push({
            cat: obj.cat,
            bis: obj.bis,
            date: Date.now()
        });
        pasador = JSON.stringify(_obj);
        $.cookie('rattedBusiness', pasador, {expires: 30});
    }
};

function closePnl(obj) {
    $(obj).hide('drop', {}, 500);
}

function postTofacebook(_obj) {
    FB.init({appId: "335214003237171", status: true, cookie: true});

    // calling the API ...
    /**
     var obj = {
        method: 'feed',
        link: link,
        picture: 'http://www.detourmaps.com/static/community/img/detourOrange.png',
        name: 'detourmaps',
        caption: 'detourmaps',
        description: 'Using Dialogs to interact with users.'
    };*/
    FB.ui(_obj, function (responce) {
    });
}

function show_hide_comments() {
    var cnt = $("#tab_review_comment")[0];
    var vlt = arguments[0] || (cnt.style['display'] == 'inline-block');
    if (vlt) {
        cnt.style['display'] = 'none';
        cnt.parentNode.style['display'] = 'inline-block';
    } else {
        cnt.style['display'] = 'inline-block';
        cnt.parentNode.style['display'] = 'block';
    }
}

var TabEvent = function () {
    if (detourmaps.tabEvent != undefined) return false;

    this.title = undefined;
    this.description = undefined;
    this.address = undefined;
    this.latlng = undefined;

    this.container = document.createElement("div");
    this.container.className = 'binfo';

    this.pnlLeft = document.createElement("div");
    this.pnlRight = document.createElement("div");

    this.cntImages = document.createElement("div");
    this.cntTitle = document.createElement("h3");
    /*<h3 style="margin-bottom: 0px;">Alan's One Stop Computer Repairs</h3>*/
    this.cntDescription = document.createElement("p");
    this.cntAddress = document.createElement("address");
    this.link_fromhere = document.createElement("a");
    this.link_tohere = document.createElement("a");

    this.facebook = document.createElement("span");
    this.twitter = document.createElement("span");
    this.google_plus = document.createElement("span");

    this.fb_a = undefined;
    this.tw_a = undefined;
    this.gp_a = undefined;
    var fb_img, tw_img;
    this.fb_a = document.createElement("a");
    this.tw_a = document.createElement("a");
    this.gp_a = document.createElement("a");

    fb_img = document.createElement("img");
    tw_img = document.createElement("img");

    fb_img.style.width = "15px";
    fb_img.style.height = "15px";
    tw_img.style.width = "15px";
    tw_img.style.height = "15px";

    fb_img.setAttribute('src', '/static/community/img/icons/ico_facebook-50x50.png');
    tw_img.setAttribute('src', '/static/community/img/icons/ico_twitter-50x50.png');

    this.fb_a.appendChild(fb_img);
    this.tw_a.appendChild(tw_img);

    this.facebook.appendChild(this.fb_a);
    this.twitter.appendChild(this.tw_a);
    this.google_plus.appendChild(this.gp_a);

    this.facebook.style.display = "none";
    this.twitter.style.display = "none";
    this.google_plus.style.display = "none";

    this.pnlLeft.setAttribute('style', 'background-color:red;position:absolute;left:6px;top:10px;');
    this.pnlLeft.className = "lpanel";
    this.pnlLeft.style.width = '215px';
    this.pnlLeft.style.height = '215px';

    this.pnlRight.setAttribute('style', 'background-color:white;position:absolute;right:6px;top:10px;');
    this.pnlRight.style.width = '215px';
    this.pnlRight.style.height = '210px';
    this.pnlRight.style.paddingLeft = '5px';

    this.cntTitle.setAttribute('style', 'margin-bottom: 0px;');
    this.cntTitle.style.fontSize = '1.1em';
    this.cntTitle.style.fontFamily = "'Arvo', Georgia, Utopia, Palatino, 'Palatino Linotype', serif";
    this.cntTitle.style.fontWeight = '700';
    this.cntTitle.style.color = '#f48131';
    this.cntTitle.style.lineHeight = '1.35em';
    this.cntTitle.style.margin = '5px 0';
    this.cntTitle.style.paddingRight = '18px';
    this.cntTitle.textContent = 'Title Event';

    this.cntDescription.style.fontSize = '0.8em';
    this.cntDescription.style.fontFamily = "'Istok Web', Verdana, sans-serif";
    this.cntDescription.style.lineHeight = '1.2em';
    this.cntDescription.style.color = '#444';
    this.cntDescription.style.marginBottom = '0.5em';

    this.cntAddress.style.marginRight = '2px';
    this.cntAddress.style.color = '#999';
    this.cntAddress.style.fontStyle = 'normal';
    this.cntAddress.style.lineHeight = '1.3em';
    this.cntAddress.style.fontSize = '0.8em';
    this.cntAddress.style.fontFamily = "'Istok Web', Verdana, sans-serif";

    this.link_fromhere.setAttribute("target", "_blank");
    this.link_fromhere.className = "from";
    this.link_fromhere.textContent = "From Here.";

    this.link_tohere.setAttribute("target", "_blank");
    this.link_tohere.className = "to";
    this.link_tohere.textContent = "To Here";

    this.cntAddress.appendChild(this.link_fromhere);
    this.cntAddress.appendChild(this.link_tohere);

    this.pnlRight.appendChild(this.cntTitle);
    var hr = document.createElement('hr');
    /*<hr style="border-color: #f48131; margin-top: 0px;">*/
    hr.setAttribute('style', 'border-color: #f48131; margin-top: 0px;');
    this.pnlRight.appendChild(hr);
    this.pnlRight.appendChild(this.cntDescription);
    this.pnlRight.appendChild(this.cntAddress);
    this.pnlRight.appendChild(document.createElement("br"));
    this.pnlRight.appendChild(this.facebook);
    this.pnlRight.appendChild(this.twitter);
    this.pnlRight.appendChild(this.google_plus);

    this.container.appendChild(this.pnlLeft);
    this.container.appendChild(this.pnlRight);
};
TabEvent.prototype.setTitle = function () {
    if (arguments.length > 0)
        this.cntTitle.textContent = arguments[0];
};
TabEvent.prototype['setTitle'] = TabEvent.prototype.setTitle;
TabEvent.prototype.setDescription = function () {
    if (arguments.length > 0)
        this.cntDescription.textContent = arguments[0];
};
TabEvent.prototype['setDescription'] = TabEvent.prototype.setDescription;
TabEvent.prototype.setAddress = function () {
    if (arguments.length > 0) {
        this.cntAddress.textContent = arguments[0];
        this.cntAddress.appendChild(document.createElement("br"));

        this.link_fromhere.setAttribute("target", "_blank");
        this.link_fromhere.className = "from";
        this.link_fromhere.style.marginRight = "10px";
        this.link_fromhere.textContent = "From Here";

        this.link_tohere.setAttribute("target", "_blank");
        this.link_tohere.className = "to";
        this.link_tohere.style.marginRight = "10px";
        this.link_tohere.style.marginLeft = "10px";
        this.link_tohere.textContent = "To Here";
        this.link_fromhere.setAttribute("href", "http://maps.google.com/maps?saddr=" + arguments[0]);
        this.link_tohere.setAttribute("href", "http://maps.google.com/maps?saddr=" + arguments[0]);

        var txt = document.createTextNode(" | ");

        this.cntAddress.appendChild(this.link_fromhere);
        this.cntAddress.appendChild(txt);
        this.cntAddress.appendChild(this.link_tohere);
    }
};
TabEvent.prototype['setAddress'] = TabEvent.prototype.setAddress;
TabEvent.prototype.setImages = function (list_img) {
    cleanList(this.pnlLeft);
    var img_container = document.createElement('div');//<div class="img-wrap"></div>
    img_container.className = "img-wrap";

    for (var i in list_img) {
        var img = document.createElement('img');
        img.setAttribute('src', list_img[i].img);
        img.className = "imgSlider";
        img_container.appendChild(img);
    }
    $(img_container).slider({width: 215, height: 215, speed: 2000, speedSlide: 350});
    this.pnlLeft.appendChild(img_container);
};
TabEvent.prototype['setImages'] = TabEvent.prototype.setImages;
TabEvent.prototype.setFacebook = function (fb_link) {
    this.fb_a.setAttribute('href', fb_link);
    if (fb_link != '' && fb_link != undefined) {
        this.facebook.style.display = "block";
    } else {
        this.facebook.style.display = "none";
    }
};
TabEvent.prototype['setFacebook'] = TabEvent.prototype.setFacebook;
TabEvent.prototype.setTwitter = function (tw_link) {
    this.tw_a.setAttribute('href', tw_link);
    this.tw_a.textContent = tw_link;
    if (tw_link != '' && tw_link != undefined) {
        this.twitter.style.display = "block";
    } else {
        this.twitter.style.display = "none";
    }
};
TabEvent.prototype['setTwitter'] = TabEvent.prototype.setTwitter;
TabEvent.prototype.setGooglePlus = function (gp_link) {
    this.gp_a.setAttribute('href', gp_link);
    this.gp_a.textContent = gp_link;
    if (gp_link != '' && gp_link != undefined) {
        this.google_plus.style.display = "block";
    } else {
        this.google_plus.style.display = "none";
    }
};
TabEvent.prototype['setGooglePlus'] = TabEvent.prototype.setGooglePlus;
TabEvent.prototype.setLatLng = function () {
};
TabEvent.prototype['setLatLng'] = TabEvent.prototype.setLatLng;

$(document).ready(function () {
    detourmaps.tabEvent = new TabEvent();
    detourmaps.eventBubble = new InfoBubble({
        borderRadius: 8,
        minWidth: 423,
        minHeight: 218
    });
    detourmaps.eventBubble.preclose = function () {
        var currentURL = document.URL;
        var splitURL = currentURL.split("?");
        if (typeof window.history.pushState == 'function') {
            window.history.replaceState({biz: "", url: splitURL[0]}, "", splitURL[0]);
            //window.location.hash = "#!/" + urlPath;
            window.history.pushState("", "Titulo", splitURL[0]);
        } else {
            //window.location.hash = "#!/" + urlPath;
            window.history.pushState("", "Titulo", splitURL[0]);
        }
        this.marker.setVisible(false);
    };

    detourmaps.eventBubble.addTab('EVENT', detourmaps.tabEvent.container);
    $(detourmaps.eventBubble.tabs_[0].tab).addClass('tab_info');
    $(detourmaps.eventBubble.tabs_[0].tab).addClass('tab_1');
});

function loadEvents() {
    for (var i in detourmaps.events) {
        var itm = new EventItem(detourmaps.events[i]);
        $("#events_box").find("ul").append(itm.item);
    }
}

function buildEventBubble(bis_evn_data) {
    try {
        bisInfo.close();
        detourmaps.eventBubble.close();
    } catch (e) {
    }

    var marker = undefined;

    var geo = bis_evn_data.geo || undefined;
    console.log(geo);
    var r = geo.slice(7, geo.length - 1).split(' ') || [];

    var latlng = new google.maps.LatLng(parseFloat(r[1]), parseFloat(r[0]));
    var content_mrk = $("#events_icon").clone()[0];
    content_mrk.style.display = "block";

    marker = new RichMarker({
        position: latlng,
        map: map,
        draggable: false,
        content: content_mrk,
        flat: true
    });
    detourmaps.tabEvent.setTitle(bis_evn_data.title);
    detourmaps.tabEvent.setDescription(bis_evn_data.description);
    detourmaps.tabEvent.setAddress(bis_evn_data.address);
    detourmaps.tabEvent.setImages(bis_evn_data.images);
    detourmaps.tabEvent.setFacebook(bis_evn_data.facebook);
    detourmaps.tabEvent.setTwitter(bis_evn_data.twitter);
    detourmaps.tabEvent.setGooglePlus(bis_evn_data.google_plus);

    detourmaps.eventBubble['marker'] = marker;
    bis_evn_data['marker'] = marker;
    if (bis_evn_data.address == '') {
        detourmaps.eventBubble.marker.setVisible(false);
    }
    detourmaps.eventBubble.open(map, detourmaps.eventBubble.marker,
        function () {
            urlChanger(null, bis_evn_data.url, tab);
            detourmaps.eventBubble.marker.setVisible(true);
        }
    );
    detourmaps.eventBubble.marker.setVisible(true);

    google.maps.event.addListener(map, 'click', function () {
        detourmaps.eventBubble.close();
    });
}

var EventItem = function (bis_evt_data) {
    var self = this;
    this.bus_name = arguments[0]['bus_name'] || undefined;
    this.date = arguments[0]['date'] || undefined;

    this.item = document.createElement('li');
    this.item.className = "onred";
    this.item.title = arguments[0]['name'];
    this.item.textContent = arguments[0]['title'] + ': ' + this.date['str'] + ' ' + ('- ' + this.date['end']) || '';
    this.item.onclick = function () {
        buildEventBubble(bis_evt_data);
        $("#events_box").removeClass("display");
    };
};

function searchEventURL(url) {
    var events = cmData.events;
    for (var i in events) {
        if (events[i].url == url) {
            console.log(events[i]);
            return events[i];
        }
    }
    return false;
}

function getBisEvents(bis_field) {
    var prop;
    for (var p in bis_field) prop = p;
    var arr = [];
    for (var i in cmData.events) {
        if (cmData.events[i][prop] == bis_field[prop]) {
            arr.push(cmData.events[i]);
        }
    }
    sortEvents([
        ['date', 'year'],
        ['date', 'month'],
        ['date', 'day']
    ], arr);
    return arr;
}

function sortEvents(fields) {
    var events = arguments[1] || cmData.events;
    events.sort(function (a, b) {
        var result = 0;
        for (var i in fields) {
            var _a, _b;
            if (fields[i].length == 1) {
                _a = a[fields[i][0]];
                _b = b[fields[i][0]];
            } else if (fields[i].length == 2) {
                _a = a[fields[i][0]][fields[i][1]];
                _b = b[fields[i][0]][fields[i][1]];
            } else if (fields[i].length == 3) {
                _a = a[fields[i][0]][fields[i][1]][fields[i][2]];
                _b = b[fields[i][0]][fields[i][1]][fields[i][2]];
            }
            result = _a - _b;
            if (result != 0) return result;
        }
    });
}

var EventBusinessList = function () {
    if (detourmaps.businessEventsList != undefined) return detourmaps.businessEventsList;
    this.events = [];
    this.container = $("div#bus_events_list ul.ul_events_list")[0];
    this.url = "";

    if (this.events.length > 0) this.setEvents(this.events);
};
EventBusinessList.prototype.setEvents = function () {
    cleanList(this.container);
    this.events = getBisEvents(arguments[0]);
    if (this.events.length > 0) {
        for (var i in this.events) {
            this.container.appendChild((new EventItem(this.events[i])).item);
        }
    } else {
        var noneEvents = document.createElement("li");
        noneEvents.innerHTML = "<h2>No Events.</h2>";
        this.container.appendChild(noneEvents);
    }
};
EventBusinessList.prototype['setEvents'] = EventBusinessList.prototype.setEvents;

