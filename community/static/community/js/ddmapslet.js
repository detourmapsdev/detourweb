/**
 * Created by Mauricio on 05/10/13.
 */
(function(){
    var version = "1.9.1";
    if (window.jQuery === undefined || window.jQuery.fn.jquery < version){
        var done = false;
        var script = document.createElement('script');
        script.src = "http://ajax.googleapis.com/ajax/libs/jquery/" + version + "/jquery.min.js";
        script.onload = script.onreadystatechange = function(){
			if (!done && (!this.readyState || this.readyState == "loaded" || this.readyState == "complete")) {
				done = true;
				initMyBookmarklet();
			}
		};
		document.getElementsByTagName("head")[0].appendChild(script);
	} else {
		initMyBookmarklet();
	}
    function initMyBookmarklet(){
        (window.myBookmarklet = function(){
            if ($("#detourmaps-search").length == 0){
                $("body").append("\
                <div id='detourmaps-search'>\
                    <form>\
                        <a id='logoMaps' href='http://detourmaps.com/'><img src='http://detourmaps.com/static/community/img/detourOrange.png'/></a>\
                        <input type='text' name='marklet-search' placeholder='Name of Business' id='searchermaps'/>\
                        <button id='send-search'>Search</button>\
                        <section>\
                            <h2></h2>\
                            <input type='text' name='urlToShare' id='urlToShare'/>\
                            <input type='text' name='emailShare' id='emailShare' placeholder='Put an email to share'/>\
                            <input type='hidden' name='hiddenBiz' id='hiddenBiz'/>\
                            <button id='shareResource'>Share</button>\
                        </section>\
                        <output></output>\
                        <a href='' id='btnCloseLet'>Close</a>\
                    </form>\
                </div>\
                <script type='text/javascript'>\
                    $(document).ready(function(){\
                        $('button#send-search').click(function(e){\
                            e.preventDefault();\
                            $.ajax({\
                                async: false,\
                                global: false,\
                                url: 'http://detourmaps.com/search-business/?marklet-search=' + $('#searchermaps').val() + '&callback=?',\
                                dataType: 'jsonp',\
                                crossdomain: true,\
                                success: function(data){\
                                    $('#detourmaps-search section').show();\
                                    $('#detourmaps-search section h2').html(data[0].name);\
                                    $('#detourmaps-search section input#urlToShare').val(data[0].url);\
                                    $('#detourmaps-search section input#hiddenBiz').val(data[0].name);\
                                },\
                                error: function(XMLHttpRequest, textStatus, errorThrown){\
                                    console.log(XMLHttpRequest + ' ' + textStatus + ' ' + errorThrown);\
                                }\
                            });\
                        });\
                        $('button#shareResource').click(function(e){\
                            e.preventDefault();\
                            $.ajax({\
                                async: false,\
                                global: false,\
                                url: 'http://detourmaps.com/share-url/?urlToShare=' + encodeURIComponent($('#urlToShare').val()) + '&hiddenBiz=' + $('#hiddenBiz').val() + '&emailShare=' + $('#emailShare').val() + '&callback=?',\
                                dataType: 'jsonp',\
                                crossdomain: true,\
                                success: function(data){\
                                    $('#detourmaps-search output').html('The URL has been shares!!1');\
                                },\
                                error: function(XMLHttpRequest, textStatus, errorThrown){\
                                    console.log(XMLHttpRequest + ' ' + textStatus + ' ' + errorThrown);\
                                }\
                            });\
                        });\
                        $('a#btnCloseLet').click(function(e){\
                            $('#detourmaps-search').hide();\
                            e.returnValue = false;\
                            return false;\
                        });\
                    })\
                </script>\
                <style type='text/css'>\
                    #detourmaps-search a#logoMaps{display: block; width: 100%; margin: 1% 1%;}\
                    #detourmaps-search a#btnCloseLet{position: absolute; bottom: 10px; display: block; padding: 8px 15px; background: #333; color: #fff; text-decoration: none; text-align: center;}\
                    #detourmaps-search{position:absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5)}\
                    #detourmaps-search form{position: absolute; top: 50%; left: 50%; width: 36%; margin-left: -20%; margin-top: -150px; background: #eee; text-align: center; padding: 100px 2%;}\
                    #detourmaps-search form input{box-sizing: border-box;-moz-box-sizing: border-box;-webkit-box-sizing: border-box;font-family: 'Istok Web', sans-serif;width: 100%;padding: 6px 12px 4px;background: #F2f4F6;outline: none;color: #666;-moz-border-radius: 2px;-webkit-border-radius: 2px;border: 1px solid #ccc;border-radius: 2px;box-shadow: inset 0 0 1px rgba(10, 143, 191, 0);-webkit-transition: all 0.3s ease-in-out;-moz-transition: all 0.3s ease-in-out;-o-transition: all 0.3s ease-in-out;transition: all 0.3s ease-in-out;}\
                    #detourmaps-search form button{width: 132px;padding: 8px 16px 6px;margin: 2px 0;color: #fff;cursor: pointer;font-family: 'Istok Web', sans-serif;background: #f48131;background: -moz-linear-gradient(top, #ffaa33 0%, #ff8833 100%);background: -webkit-linear-gradient(top, #ffaa33 0%, #ff8833 100%);background: -o-linear-gradient(top, #ffaa33 0%, #ff8833 100%);background: -ms-linear-gradient(top, #ffaa33 0%, #ff8833 100%);filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#ffaa33', endColorstr='#ff8833', GradientType=0);border: 1px #f48131 solid;border-radius: 4px;-moz-border-radius: 4px;-webkit-border-radius: 4px;}\
                    #detourmaps-search section{display: none;}\
                </style>");
            }
            else{
                $('#detourmaps-search').show();
            }
        })();
    }
})();
