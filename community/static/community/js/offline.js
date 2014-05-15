/**
 * @author Mauricio
 */
var html5rocks = {};
window.indexedDB = window.indexedDB || window.webkitIndexedDB ||
    window.mozIndexedDB;

if ('webkitIndexedDB' in window) {
    window.IDBTransaction = window.webkitIDBTransaction;
    window.IDBKeyRange = window.webkitIDBKeyRange;
}

html5rocks.indexedDB = {};
html5rocks.indexedDB.db = null;
html5rocks.indexedDB.dbBiz = null;

html5rocks.indexedDB.onerror = function (e) {
    console.log(e);
};
html5rocks.indexedDB.open = function (e) {
    var version = 1;
    var request = indexedDB.open("detourMapsDB", version);
    request.onupgradeneeded = function (e) {
        var db = e.target.result;
        e.target.transaction.onerror = html5rocks.indexedDB.onerror;
        if (db.objectStoreNames.contains("user")) {
            db.deleteObjectStore("user");
        }
        var objectStore = db.createObjectStore("user", { keyPath: "id", autoIncrement: true});
        objectStore.createIndex("firstname", "firstname", { unique: false });
        objectStore.createIndex("lastname", "lastname", { unique: false });
        objectStore.createIndex("address", "address", { unique: false });
        objectStore.createIndex("city", "city", { unique: false });
        objectStore.createIndex("state", "state", { unique: false });
        objectStore.createIndex("zipcode", "zipcode", { unique: false });
        objectStore.createIndex("phone", "phone", { unique: false });
        objectStore.createIndex("cell", "cell", { unique: false });
        objectStore.createIndex("email", "email", { unique: false });
        objectStore.createIndex("website", "website", { unique: false });
        objectStore.createIndex("yes", "yes", { unique: false });
        objectStore.createIndex("no", "no", { unique: false });
    };
    request.onsuccess = function (e) {
        html5rocks.indexedDB.db = e.target.result;
    };
    request.onerror = html5rocks.indexedDB.onerror;
    var requestBiz = indexedDB.open("detourMapsDBBiz", version);
    requestBiz.onupgradeneeded = function (e) {
        var dbBiz = e.target.result;
        e.target.transaction.onerror = html5rocks.indexedDB.onerror;
        if (dbBiz.objectStoreNames.contains("biz")) {
            dbBiz.deleteObjectStore("biz");
        }
        var objectStore = dbBiz.createObjectStore("biz", { keyPath: "id", autoIncrement: true});
        objectStore.createIndex("name", "name", { unique: false });
        objectStore.createIndex("address", "address", { unique: false });
        objectStore.createIndex("owner", "owner", { unique: false });
        objectStore.createIndex("city", "city", { unique: false });
        objectStore.createIndex("state", "state", { unique: false });
        objectStore.createIndex("zipcode", "zipcode", { unique: false });
        objectStore.createIndex("phone", "phone", { unique: false });
        objectStore.createIndex("cell", "cell", { unique: false });
        objectStore.createIndex("email", "email", { unique: false });
        objectStore.createIndex("website", "website", { unique: false });
        objectStore.createIndex("category", "category", {unique: false});
        objectStore.createIndex("types", "types", {unique: false});
        objectStore.createIndex("tactics", "tactics", {unique: false});
        objectStore.createIndex("planned", "planned", {unique: false});
        objectStore.createIndex("freq", "freq", {unique: false});
        objectStore.createIndex("month", "month", {unique: false});
    };
    requestBiz.onsuccess = function (e) {
        html5rocks.indexedDB.dbBiz = e.target.result;
    };
    requestBiz.onerror = html5rocks.indexedDB.onerror;
};
function init() {
    html5rocks.indexedDB.open();
}
$(document).ready(function () {
    init();
    $("#save").click(function (e) {
        e.preventDefault();
        if (navigator && navigator.onLine === false) {
            var transaction = "";
            transaction = html5rocks.indexedDB.db.transaction(["user"], "readwrite").objectStore("user")
                .add({
                    firstname: $("#firstname").val(),
                    lastname: $("#lastname").val(),
                    address: $("#address").val(),
                    city: $("#city").val(),
                    state: $("#state").val(),
                    zipcode: $("#zip").val(),
                    phone: $("#phone").val(),
                    cell: $("#cellphone").val(),
                    email: $("#email").val(),
                    website: $("#web").val()
                });
            transaction.onsuccess = function () {
                $("#firstname").val("");
                $("#lastname").val("");
                $("#address").val("");
                $("#city").val("");
                $("#state").val("");
                $("#zip").val("");
                $("#phone").val("");
                $("#cellphone").val("");
                $("#email").val("");
                $("#web").val("");
            }
            var category = $("input[name='category']:checked").val();
            var valCat;
            var catArray = [];
            if (category != 'other') {
                valcat = category;
            }
            else {
                valcat = $("#otherC").val();
            }
            var types = $("input[name='types']:checked").val();
            var valType;
            if (types != 'random') {
                $("input[name='types']:checked").each(function () {
                    catArray.push($(this).val());
                });
                valType = catArray;
            } else {
                valType = $("#otherT").val();
            }
            var tactics = $("input[name='mkt']:checked").val();
            var valTactics;
            var tacticArray = [];
            if (tactics != 'mkt') {
                $("input[name='mkt']:checked").each(function () {
                    tacticArray.push($(this).val());
                });
                valTactics = tacticArray;
            } else {
                valTactics = $("#otherM").val();
            }
            var plannedArray = [];
            $("input[name='conduct']:checked").each(function () {
                plannedArray.push($(this).val());
            });
            var freqArray = [];
            $("input[name='freq']:checked").each(function () {
                freqArray.push($(this).val());
            });
            var months = $("input[name='month']:checked").val();
            var valMonths;
            var monthsArray = [];
            if (months != 'All') {
                $("input[name='month']:checked").each(function () {
                    monthsArray.push($(this).val());
                });
                valMonths = monthsArray;
            } else {
                valMonths = "All";
            }
            var transactionBiz = "";
            transaction = html5rocks.indexedDB.dbBiz.transaction(["biz"], "readwrite").objectStore("biz")
                .add({
                    name: $("#business").val(),
                    address: $("#addressB").val(),
                    owner: $("#owner").val(),
                    city: $("#cityB").val(),
                    state: $("#stateB").val(),
                    zipcode: $("#zipB").val(),
                    phone: $("#phoneB").val(),
                    cell: $("#phoneB").val(),
                    email: $("#emailB").val(),
                    website: $("#webB").val(),
                    category: valcat,
                    types: valType,
                    tactics: valTactics,
                    planned: plannedArray,
                    freq: freqArray,
                    month: valMonths
                });
            transaction.onsuccess = function () {
                $("#business").val("");
                $("#owner").val("");
                $("#addressB").val("");
                $("#cityB").val("");
                $("#stateB").val("");
                $("#zipB").val("");
                $("#phoneB").val("");
                $("#cellphoneB").val("");
                $("#emailB").val("");
                $("#webB").val("");
                $("input[name='category']:checked").each(function () {
                    $(this).checked = false;
                });
            }
        }
        else {
            var transaction = "";
            transaction = html5rocks.indexedDB.db.transaction(["user"], "readwrite");
            var objectStore = transaction.objectStore("user");
            var request = objectStore.openCursor();
            request.onsuccess = function (evt) {
                cursor = evt.target.result;
                if (cursor) {
                    console.log(cursor.value.firstname);
                    $.post('/registerUserAjax/', {
                        firstname: cursor.value.firstname,
                        lastname: cursor.value.lastname,
                        address: cursor.value.address,
                        city: cursor.value.city,
                        state: cursor.value.state,
                        zip: cursor.value.zipcode,
                        phone: cursor.value.phone,
                        cell: cursor.value.cell,
                        email: cursor.value.email,
                        website: cursor.value.website,
                        suscribe: 1
                    }, function (data) {
                        console.log(data);
                    });
                    cursor.continue();
                }
                else {
                    console.log("nothing");
                }
            }
            var transactionBiz = "";
            transactionBiz = html5rocks.indexedDB.dbBiz.transaction(["biz"], "readwrite");
            var objectStoreBiz = transactionBiz.objectStore("biz");
            var requestBiz = objectStoreBiz.openCursor();
            requestBiz.onsuccess = function (evt) {
                cursor = evt.target.result;
                if (cursor) {
                    console.log(cursor.value.types);
                    $.post('/registerAjax/', {
                        name: cursor.value.name,
                        address: cursor.value.address,
                        owner: cursor.value.owner,
                        city: cursor.value.city,
                        state: cursor.value.state,
                        zip: cursor.value.zipcode,
                        phone: cursor.value.phone,
                        cell: cursor.value.cell,
                        email: cursor.value.email,
                        website: cursor.value.website,
                        category: cursor.value.category,
                        types: JSON.stringify(cursor.value.types),
                        tactics: JSON.stringify(cursor.value.tactics),
                        planned: JSON.stringify(cursor.value.planned),
                        freq: JSON.stringify(cursor.value.freq),
                        month: JSON.stringify(cursor.value.month)
                    }, function (data) {
                        console.log(data);
                    });
                    cursor.continue();
                }
                else {
                    console.log("nothing");
                }
            }
        }

    });
});
