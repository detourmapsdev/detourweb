/**
 * User: Juan Manuel Ticona Pacheco
 * Date: 01/11/12
 */
tinyMCE.init({
    // General options
    mode : "exact",
    elements : "{{textarea_id}}",
    theme : "advanced",
    plugins : "autolink,lists,spellchecker,pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template",
    height: "800",
    // Theme options
    theme_advanced_buttons1 : "save,newdocument,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,|,styleselect,formatselect,fontselect,fontsizeselect",
    theme_advanced_buttons2 : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor",
    theme_advanced_buttons3 : "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen",
    theme_advanced_buttons4 : "insertlayer,moveforward,movebackward,absolute,|,styleprops,spellchecker,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,nonbreaking,template,blockquote,pagebreak,|,insertfile,insertimage",
    theme_advanced_toolbar_location : "top",
    theme_advanced_toolbar_align : "left",
    theme_advanced_statusbar_location : "bottom",
    theme_advanced_resizing : true,

    // Skin options
    skin : "o2k7",
    skin_variant : "black",

    // Example content CSS (should be your site CSS)
    content_css : "css/example.css",

    relative_urls : false,
    remove_script_host : false,
    document_base_url : "http://localhost:8000/",
    // Drop lists for link/image/media/template dialogs
    external_link_list_url : "js/link_list.js",
    external_image_list_url : "/news/list",
    media_external_list_url : "js/media_list.js",

    // Replace values for the template plugin
    template_replace_values : {
        username : "Some User",
        staffid : "991234"
    },
    file_browser_callback: function(field_name, url, type, win){

        /* If you work with sessions in PHP and your client doesn't accept cookies you might need to carry
         the session name and session ID in the request string (can look like this: "?PHPSESSID=88p0n70s9dsknra96qhuk6etm5").
         These lines of code extract the necessary parameters and add them back to the filebrowser URL again. */

        /* Here goes the URL to your server-side script which manages all file browser things. */
        var ventana = window.open('/news/form',null,'width=600,height=150');
        ventana.tinymceFileField = field_name;
        ventana.tinymceFileWin = win;
    },
    forced_root_block : false,
    force_br_newlines : true,
    force_p_newlines : true
});