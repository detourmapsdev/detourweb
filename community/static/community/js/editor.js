/**
 * Created with PyCharm.
 * User: mauricio
 * Date: 17/07/12
 * Time: 03:14 PM
 * To change this template use File | Settings | File Templates.
 */
var progress;
var sourceFlag = true;
var ctrlDown = false;
var ctrlKey = 17, vKey = 86, cKey = 67;
function fontEdit(x, y, el) {
    var id = el.parent().next().attr("idb");
    var textEditor = document.getElementById(id).contentWindow;
    textEditor.document.execCommand(x, "", y);
    textEditor.focus();
}
function insertHtml(x, y, el) {
    var id = el.parent().next().attr("idb");
    var textEditor = document.getElementById(id).contentWindow;
    textEditor.document.execCommand(x, "", y);
    textEditor.focus();
}
function insertURL(el) {
    var id = el.parent().next().attr("idb");
    var textEditor = document.getElementById(id).contentWindow;
    var urlPrompt = prompt("Ingrese una dirección web", "http://");
    if((urlPrompt != null) && (urlPrompt != "")){
        textEditor.document.execCommand('CreateLink', false, urlPrompt);
        textEditor.focus();
    }
}
function viewSource(el) {
    var id = el.parent().next().attr("idb");
    var textEditor = document.getElementById(id).contentWindow;
    var html;
    if(sourceFlag){
        html = document.createTextNode(document.getElementById(id).contentWindow.document.body.innerHTML);
        document.getElementById(id).contentWindow.document.body.innerHTML = "";
        html = document.getElementById(id).contentWindow.document.importNode(html, false);
        document.getElementById(id).contentWindow.document.body.appendChild(html);
        //textEditor.focus();
        sourceFlag = false;
    }else{
        html = document.getElementById(id).contentWindow.document.body.ownerDocument.createRange();
        html.selectNodeContents(document.getElementById(id).contentWindow.document.body);
        document.getElementById(id).contentWindow.document.body.innerHTML = html.toString();
        //textEditor.focus();
        sourceFlag = false;
    }
}
function formatVal(val, el) {
    var id = el.parent().next().attr("idb");
    var textEditor = document.getElementById(id).contentWindow;
    textEditor.document.execCommand('formatblock', false, val);
    textEditor.focus();
}
function pInsteadDiv(val, el) {
    var textEditor = document.getElementById(el).contentWindow;
    textEditor.document.execCommand('formatValblock', false, val);
    textEditor.focus();
}
function insertNodeAtSelection(win, insertNode) {
    // get current selection
    var sel = win.getSelection();

    // get the first range of the selection
    // (there's almost always only one range)
    var range = sel.getRangeAt(0);

    // deselect everything
    sel.removeAllRanges();

    // remove content of current selection from document
    range.deleteContents();

    // get location of current selection
    var container = range.startContainer;
    var pos = range.startOffset;

    // make a new range for the new selection
    range = document.createRange();

    if (container.nodeType == 3 && insertNode.nodeType == 3) {

        // if we insert text in a textnode, do optimized insertion
        container.insertData(pos, insertNode.nodeValue);

        // put cursor after inserted text
        range.setEnd(container, pos + insertNode.length);
        range.setStart(container, pos + insertNode.length);

    } else {


        var afterNode;
        if (container.nodeType == 3) {

            // when inserting into a textnode
            // we create 2 new textnodes
            // and put the insertNode in between

            var textNode = container;
            container = textNode.parentNode;
            var text = textNode.nodeValue;

            // text before the split
            var textBefore = text.substr(0, pos);
            // text after the split
            var textAfter = text.substr(pos);

            var beforeNode = document.createTextNode(textBefore);
            afterNode = document.createTextNode(textAfter);

            // insert the 3 new nodes before the old one
            container.insertBefore(afterNode, textNode);
            container.insertBefore(insertNode, afterNode);
            container.insertBefore(beforeNode, insertNode);

            // remove the old node
            container.removeChild(textNode);

        } else {

            // else simply insert the node
            afterNode = container.childNodes[pos];
            container.insertBefore(insertNode, afterNode);
        }

        range.setEnd(afterNode, 0);
        range.setStart(afterNode, 0);
    }

    sel.addRange(range);
}

function insertTable(el) {
    var id = el.parent().next().attr("idb");
    var textEditor = document.getElementById(id).contentWindow;
    rowstext = prompt("ingresar filas");
    colstext = prompt("ingresar columnas");
    rows = parseInt(rowstext);
    cols = parseInt(colstext);
    if ((rows > 0) && (cols > 0)) {
        table = textEditor.document.createElement("table");
        table.setAttribute("border", "1");
        table.setAttribute("cellpadding", "2");
        table.setAttribute("cellspacing", "2");
        tbody = textEditor.document.createElement("tbody");
        for (var i = 0; i < rows; i++) {
            tr = textEditor.document.createElement("tr");
            for (var j = 0; j < cols; j++) {
                td = textEditor.document.createElement("td");
                br = textEditor.document.createElement("br");
                td.appendChild(br);
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }
        table.appendChild(tbody);
        textEditor.document.body.appendChild(table);
        console.log(table);
        textEditor.focus();
    }
}

function YouTube(el) {
    var id = el.parent().next().attr("idb");
    var textEditor = document.getElementById(id).contentWindow;
    var urlPrompt = prompt("Ingrese la dirección hacia un video en YouTube", "http://")
    var urlReplace = urlPrompt.replace("watch?v=", "embed/");
    var urlSplit = urlReplace.split("&");
    var embed = '<iframe title="YouTube video player" src="' + urlSplit[0] + '" allowfullscreen="true" width="480" frameborder="0" height="390"></iframe>';
    if ($.browser.msie) {
        textEditor.document.createRange().pasteHTML(embed)
    } else {
        textEditor.document.execCommand("Inserthtml", false, embed);
    }
    textEditor.focus();
}
function InsertImage(el) {
    var id = el.parent().next().attr("idb");
    var textEditor = document.getElementById(id).contentWindow;
    el.parent().next().find(".upload").slideToggle();
    textEditor.focus();
}
function uploadComplete(evt) {
    var textEditor = document.getElementById('textEditor').contentWindow;
    var embed = '<img src="' + evt.target.response + '" class="thumb"/>';
    if ($.browser.msie) {
        textEditor.document.createRange().pasteHTML(embed)
    } else {
        textEditor.document.execCommand("Inserthtml", false, embed);
    }
    progress.style.width = '100%';
    progress.textContent = '100%';
}
function uploadFile(data, file) {
    var formData = new FormData();
    progress.style.width = '0%';
    progress.textContent = '0%';
    formData.append('data', data);
    formData.append('name', file);
    var xhr = new XMLHttpRequest();
    xhr.upload.addEventListener("progress", function (e) {
        var pc = Math.round((e.loaded / e.total) * 100);
        if (pc < 100) {
            progress.style.width = pc + '%';
            progress.textContent = pc + '%';
        }
    }, false);
    xhr.addEventListener("load", uploadComplete, false);
    xhr.onreadystatechange = function (e) {
        if (xhr.readyState == 4) {
            progress.className = (xhr.status == 200 ? "success" : "failure");
            if (progress.className == "success") {
                progress.style.width = '0%';
                progress.textContent = '0%';
            }
        }
    };
    xhr.open('POST', '/home/upload/', true);
    xhr.send(formData);
    return false;
}
function htmlTextArea(el) {
    var splitId = el.split("-");
    var html1 = $("#editor-" + el).contents().find('body').html();
    document.getElementById(el).value = html1;
}
function htmlTextAreaToIFrame(el) {
    var html1 = document.getElementById(el).value;
    $("#editor-" + el).contents().find('body').html(html1);
}

function upload(url, files, el) {
    var id = el.parent().parent().attr("idb");
    var textEditor = document.getElementById(id).contentWindow;
    percent = el.parent().find(".percent");
    percent.parent().show();
    var formdata = new FormData();
    for (var x = 0, file; file = files[x]; x++) {
        formdata.append('file', file);
    }
    var xhr = new XMLHttpRequest();
    xhr.upload.addEventListener("progress", function (e) {
        var pc = Math.round((e.loaded / e.total) * 100);
        if (pc < 100) {
            percent.animate({'width': pc + '%'});
            percent.text(pc + '%');
        }
    }, false);
    xhr.onreadystatechange = function (e) {
        if (xhr.readyState == 4) {
            progress.className = (xhr.status == 200 ? "success" : "failure");
            if (progress.className == "success") {
                percent.animate({'width': '100%'});
                percent.text('100%');
            }
        }
    };
    xhr.open('POST', url, true);
    xhr.onload = function (e) {
        var embed = '<img src=' + e.target.response + ' class="thumb"/>';
        if ($.browser.msie) {
            textEditor.document.createRange().pasteHTML(embed)
        } else {
            textEditor.document.execCommand("Inserthtml", false, embed);
        }
        textEditor.focus();
    };
    xhr.send(formdata);
}

function cleanup(texto) {
    var tmp = document.createElement("P");
    var strClean = texto.toString().replace(/<\/?[^>]+>/gi, '');
    strClean = strClean.replace(/"/gi, '').replace(/'/gi, '');
    var textNew = document.createTextNode(strClean);
    tmp.appendChild(textNew);
    return tmp;
}
$(document).keydown(function (e) {
    if (e.keyCode == ctrlKey) ctrlDown = true;
    console.log(ctrlDown);
}).keyup(function (e) {
        if (e.keyCode == ctrlKey) ctrlDown = false;
    });
(function ($) {

    $.fn.myeditor = function (options) {

        var settings = $.extend({
            'width': '720',
            'height': '470',
            'url': '/home/upload/'
        }, options);
        return this.each(function () {
            $(this).hide();
            var id = $(this).attr("id");
            var listMenu = '<button id="table-' + id + '" class="table icon-table" title="Tabla"></button>' +
                '<button id="bold-' + id + '" class="font-bold icon-bold" title="Negrita"></button>' +
                '<button id="italic-' + id + '" class="italic icon-italic" title="Itálica"></button>' +
                '<button id="underline-' + id + '" class="underline icon-underline" title="Subrayado"></button>' +
                '<button id="strike-' + id + '" class="strike icon-strikethrough" title="Marcar"></button>' +
                '<button id="left-' + id + '" class="left icon-align-left" title="Left"></button>' +
                '<button id="center-' + id + '" class="center icon-align-center" title="Center"></button>' +
                '<button id="right-' + id + '" class="right icon-align-right" title="Right"></button>' +
                '<button id="sort-' + id + '" class="sort-list icon-list-ol" title="Lista Ordenada"></button>' +
                '<button id="unsort-' + id + '" class="unsort-list icon-list-ul" title="Lista Desordenada"></button>' +
                '<button id="outdent-' + id + '" class="oudent-list icon-indent-right" title="Quitar indentado"></button>' +
                '<button id="indent-' + id + '" class="indent-list icon-indent-left" title="Indentar"></button>' +
                '<button id="paragraph-' + id + '" class="paragraph" title="Párrafo">¶</button>' +
                '<button id="link-' + id + '" class="link icon-link" title="Crear link"></button>' +
                '<button id="youtube-' + id + '" class="youtube icon-film" title="Video"></button>' +
                '<button id="image-' + id + '" class="image icon-picture" title="Insertar Imagen"></button>' +
                '<button id="source-' + id + '" class="source icon-edit" title="Ver HTML">HTML</button>' +
                '<button id="h1-' + id + '" class="source" idb ="h1" title="H1">H1</button>' +
                '<button id="h2-' + id + '" class="source" idb ="h1" title="H2">H2</button>' +
                '<button id="h3-' + id + '" class="source" idb ="h1" title="H3">H3</button>' +
                '<button id="h4-' + id + '" class="source" idb ="h1" title="H4">H4</button>' +
                '<button id="h5-' + id + '" class="source" idb ="h1" title="H5">H5</button>' +
                '<button id="h6-' + id + '" class="source" idb ="h1" title="H6">H6</button>' +
                '<button id="pre-' + id + '" class="pre" idb ="pre" title="Code">pre</button>' +
                '<button id="undo-' + id + '" class="undo icon-undo" idb ="undo" title="Deshacer"></button>' +
                '<button id="redo-' + id + '" class="repeat icon-repeat" idb ="repeat" title="Rehacer"></button>';
            var container = "<div class='editor' style='width:" + settings.width + "px;'><div class='tabHeader' style'width:" + settings.width + "px;'>" + listMenu + "</div><div idb='editor-" + id + "'><div class='upload' style='display: none; width: 100%;'><input type='file' class='files' name='file' id='files-" + id + "'/><div class='list'></div><div class='progress'><div class='percent'>0%</div></div></div><iframe id='editor-" + id + "' style='width:" + settings.width + "px; height:" + settings.height + "px;'></iframe></div></div>";
            $(container).insertBefore("#" + id);
            var textEditor = document.getElementById('editor-' + id).contentWindow;
            textEditor.document.designMode = "on";
            textEditor.document.open();
            textEditor.document.write('<head><style type="text/css">body{ font-family:arial; font-size:12px;} button{font-family: "Helvetica"; font-size: 10px; padding: 2px; position:relative; display:inline-block;}</style> </head>');
            textEditor.document.close();
            var inputFile = 'files-' + id;
            input = document.getElementById(inputFile);
            editor = document.getElementById('editor-' + id);
            editor.contentWindow.onkeyup = function (e) {
                if (e.which == 13) {
                    pInsteadDiv('<p>', 'editor-' + id);
                }
            }
            if (input.addEventListener) {
                input.addEventListener('change', function (e) {
                    upload(settings.url, this.files, $(this));
                }, false);
            }
            else {
                input.attachEvent('change', function (e) {
                    upload(settings.url, this.files, $(this));
                });
            }
            if (editor.addEventListener) {
                editor.contentWindow.addEventListener('focus', function (e) {
                    htmlTextArea(id);
                }, true);
                editor.contentWindow.addEventListener('keyup', function (e) {
                    htmlTextArea(id);
                }, true);
                /*editor.contentWindow.addEventListener('paste',function(e){

                 if (/text\/html/.test(e.clipboardData.types)) {
                 var textPaste = cleanup(e.clipboardData.getData('text/html'));
                 if (e.preventDefault) {
                 e.preventDefault();
                 $("#editor-" + id).contents().find('body').html(textPaste);
                 } else {
                 e.returnValue = false;
                 $("#editor-" + id).contents().find('body').html(textPaste);
                 }

                 }
                 else if (/text\/plain/.test(e.clipboardData.types)) {
                 var textPaste = cleanup(e.clipboardData.getData('text/html'));
                 if (e.preventDefault) {
                 e.preventDefault();
                 $("#editor-" + id).contents().find('body').html(textPaste);
                 } else {
                 e.returnValue = false;
                 $("#editor-" + id).contents().find('body').html(textPaste);
                 }
                 }
                 else {
                 textEditor.innerHTML = "";
                 }
                 return false;
                 }, true);*/
                htmlTextAreaToIFrame(id);
            }
            else {
                editor.contentWindow.attachEvent('onfocus', function (e) {
                    htmlTextArea(id);
                }, true);
                editor.contentWindow.attachEvent('onkeyup', function (e) {
                    htmlTextArea(id);
                }, true);
                editor.contentWindow.attachEvent('onpaste', function (e) {
                    console.log(e);
                }, true);
                htmlTextAreaToIFrame(id);
            }
            progress = document.querySelector('.percent');
            $("#table-" + id).click(function (e) {
                insertTable($(this));
                e.returnValue = false;
                return false;
            });
            $("#bold-" + id).click(function (e) {
                fontEdit('bold', '', $(this));
                e.returnValue = false;
                return false;
            });
            $("#italic-" + id).click(function (e) {
                fontEdit('italic', '', $(this));
                e.returnValue = false;
                return false;
            });
            $("#underline-" + id).click(function (e) {
                fontEdit('underline', '', $(this));
                e.returnValue = false;
                return false;
            });
            $("#strike-" + id).click(function (e) {
                fontEdit('StrikeThrough', '', $(this));
                e.returnValue = false;
                return false;
            });
            $("#left-" + id).click(function (e) {
                fontEdit('justifyleft', '', $(this));
                e.returnValue = false;
                return false;
            });
            $("#right-" + id).click(function (e) {
                fontEdit('justifyright', '', $(this));
                e.returnValue = false;
                return false;
            });
            $("#center-" + id).click(function (e) {
                fontEdit('justifycenter', '', $(this));
                e.returnValue = false;
                return false;
            });
            $("#sort-" + id).click(function (e) {
                fontEdit('insertorderedlist', '', $(this));
                e.returnValue = false;
                return false;
            });
            $("#unsort-" + id).click(function (e) {
                fontEdit('insertunorderedlist', '', $(this));
                e.returnValue = false;
                return false;
            });
            $("#outdent-" + id).click(function (e) {
                fontEdit('outdent', '', $(this));
                e.returnValue = false;
                return false;
            });
            $("#indent-" + id).click(function (e) {
                fontEdit('indent', '', $(this));
                e.returnValue = false;
                return false;
            });
            $("#paragraph-" + id).click(function (e) {
                formatVal('<p>', $(this));
                e.returnValue = false;
                return false;
            });
            $("#h1-" + id).click(function (e) {
                formatVal('<h1>', $(this));
                e.returnValue = false;
                return false;
            });
            $("#h2-" + id).click(function (e) {
                formatVal('<h2>', $(this));
                e.returnValue = false;
                return false;
            });
            $("#h3-" + id).click(function (e) {
                formatVal('<h3>', $(this));
                e.returnValue = false;
                return false;
            });
            $("#h4-" + id).click(function (e) {
                formatVal('<h4>', $(this));
                e.returnValue = false;
                return false;
            });
            $("#h5-" + id).click(function (e) {
                formatVal('<h5>', $(this));
                e.returnValue = false;
                return false;
            });
            $("#h6-" + id).click(function (e) {
                formatVal('<h6>', $(this));
                e.returnValue = false;
                return false;
            });
            $("#link-" + id).click(function (e) {
                insertURL($(this));
                e.returnValue = false;
                return false;
            });
            $("#youtube-" + id).click(function (e) {
                YouTube($(this));
                e.returnValue = false;
                return false;
            });
            $("#image-" + id).click(function (e) {
                InsertImage($(this));
                e.returnValue = false;
                return false;
            });
            $("#source-" + id).click(function (e) {
                viewSource($(this));
                e.returnValue = false;
                return false;
            });
            $("#pre-" + id).click(function (e) {
                formatVal('<pre>', $(this));
                e.returnValue = false;
                return false;
            });
            $("#undo-" + id).click(function (e) {
                fontEdit('Undo', '', $(this));
                e.returnValue = false;
                return false;
            });
            $("#redo-" + id).click(function (e) {
                fontEdit('StrikeThrough', '', $(this));
                e.returnValue = false;
                return false;
            });
        });
    }
})(jQuery);