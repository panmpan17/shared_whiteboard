function format() {
	var s = arguments[0];
	for (var i = 0; i < arguments.length - 1; i++) {       
		var reg = new RegExp("\\{" + i + "\\}", "gm");             
		s = s.replace(reg, arguments[i + 1]);
	}
	return s;
}

function storeCookie(cname, value) {
    f = "{0}={1}; path=/"
    document.cookie = format(f, cname, value);
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for(var i=0; i<ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1);
        if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
    }
    return "";
}

function deleteCookie (cname) {
    document.cookie = cname + "=; path=/";
}

function parse (text) {
    args = {}
    args_text = text.split("&")

    $.each(args_text, function (_, i) {
        equl = i.indexOf("=")
        key = i.substring(0, equl)
        value = i.substring(equl + 1)
        args[key] = value
    })

    return args
}

function make_header (args) {
    header = []

    $.each(args, function (key, value) {
        header.push(format("{0}={1}", key, value))
    })

    return header.join("&")
}