GET = "GET"
POST = "POST"
PUT = "PUT"

UNDO = "UNDO"
REDO = "REDO"

var layers = [];
var layer_ctxes = [];
var bg_contains = [];
var layer_contains = [];
var stroke_points = [];

var stroke_size = 5
var radius = 3;
var drawing = false;
var isDrawing = false;
var posting = false;
var lastpoint = [null, null];
var layer_limit = 5
var board_id = null

socket = null

$(document).ready(function () {
	try {
		socket = new WebSocket("ws://" + window.location.hostname + ":21085")
	} catch (e) {
		alert("Cannot connect to server, please try again later.")
	}

	bg = document.getElementById("background")
	ctx_bg = bg.getContext("2d")
	draw = document.getElementById("drawing")
	ctx_draw = draw.getContext("2d")

	WIDTH = draw.width;
	HEIGHT = draw.height;

	ctx_bg.strokeStyle = "red";
	ctx_bg.lineWidth = "5";

	board_id = window.location.pathname.replace("/draw/", "")

	socket.onmessage = function (e) {
		args = parse(e.data)

		if (args["method"] == GET) {
			if (args["success"] == "False") {
				alert(args["reason"])
				return;
			}
			args["layer_num"] = parseInt(args["layer_num"])
			layer_limit = args["layer_num"]
			html = ""
			for (i=0;i<args["layer_num"];i++) {
				html += format(
					`<canvas id="layer{0}" width="720" height="540"></canvas>`,
					i + 1)
			}
			$("#layers").html(html)
			findalllayer();

			layers_string = args["layers"].split("|")
			layers_string.pop()
			$.each(layers_string, function (_, i) {
				if (i == "") {
					layer_contains.push(undefined)
					return true;
				}
				layer_contains.push(parse_storke_string(i))
			})

			redraw();

			layers_string = args["bg"].split("|")
			layers_string.pop()
			$.each(layers_string, function (_, i) {
				bg_stroke = parse_storke_string(i)
				bg_contains.push(bg_stroke)

				ctx_bg.strokeStyle = bg_stroke["color"];
				ctx_bg.lineWidth = bg_stroke["size"];

				if (bg_stroke["points"].length == 0) {
					return true;
				}

				ctx_bg.beginPath();
				ctx_bg.moveTo(bg_stroke["points"][0][0], bg_stroke["points"][0][1]);

				for (e=1;e<bg_stroke["points"].length;e++) {
					ctx_bg.lineTo(bg_stroke["points"][e][0], bg_stroke["points"][e][1]);
				}
				ctx_bg.stroke();
			})
		}
		else if (args["method"] == "POST") {
			posting = false;

			if (layer_contains[0] != undefined) {
				bg_contains.push(layer_contains[0])

				stroke = layer_contains[0]
				ctx_bg.strokeStyle = stroke["color"];
				ctx_bg.lineWidth = stroke["size"];

				if (stroke["points"].length != 0) {
					ctx_bg.beginPath();
					ctx_bg.moveTo(stroke["points"][0][0], stroke["points"][0][1]);

					for (e=1;e<stroke["points"].length;e++) {
						ctx_bg.lineTo(stroke["points"][e][0], stroke["points"][e][1]);
					}
					ctx_bg.stroke();
				}
			}

			stroke = parse_storke_string(args["stroke"])
			layer_contains.push(stroke)
			console.log(layer_contains)
			layer_contains = layer_contains.slice(1)
			console.log(layer_contains)

			redraw();
		}
		else if (args["method"] == "PUT") {
			posting = false;
			if (args["action"] == UNDO) {
				layer_contains.pop()
				layer_contains.unshift(undefined)
				redraw()
			}
		}
	}

	socket.onopen = function () {
		args = {
			"method": GET,
			"board_id": board_id,
		}
		socket.send(make_header(args))
	}

	socket.onclose = function (e) {
		alert("Cannot connect to server, please try again later.")
	};

	draw.addEventListener('mousedown', function(event) {
		if (!posting) {
			isDrawing = true;
			lastpoint = [event.offsetX, event.offsetY];
			stroke_points.push(lastpoint)
		}
	})

	draw.addEventListener('mousemove', function(event) {
		if (isDrawing) {
			ctx_draw.strokeStyle = "red";
			ctx_draw.lineWidth = String(stroke_size);
			ctx_draw.beginPath();

			ctx_draw.moveTo(lastpoint[0], lastpoint[1]);
			ctx_draw.lineTo(event.offsetX, event.offsetY);
			lastpoint = [event.offsetX, event.offsetY]
			stroke_points.push(lastpoint)
			ctx_draw.stroke();;
		}
	})

	draw.addEventListener('mouseup', function(event) {
		isDrawing = false

		ctx_draw.clearRect(0, 0, WIDTH, HEIGHT);

		args = {
			"method": "POST",
			"stroke": stroke_2_string(stroke_size,
				"red",
				stroke_points),
			"board_id": board_id,
		}

		stroke_points = []
		posting = true;
		socket.send(make_header(args))
	})

	draw.addEventListener('touchstart', function(event) {
		if (!posting) {
			isDrawing = true;
			touch = event.touches[0];
			lastpoint = [touch.clientX, touch.clientY];
			stroke_points.push(lastpoint)
		}
	})

	draw.addEventListener('touchmove', function(event) {
		if (isDrawing) {
			ctx_draw.strokeStyle = "red";
			ctx_draw.lineWidth = String(stroke_size);
			ctx_draw.beginPath();

			ctx_draw.moveTo(lastpoint[0], lastpoint[1]);
			touch = event.touches[0];
			ctx_draw.lineTo(touch.clientX, touch.clientY);
			lastpoint = [touch.clientX, touch.clientY]
			stroke_points.push(lastpoint)
			ctx_draw.stroke();;
		}
	})

	draw.addEventListener('touchend', function(event) {
		isDrawing = false

		ctx_draw.clearRect(0, 0, WIDTH, HEIGHT);

		args = {
			"method": "POST",
			"stroke": stroke_2_string(stroke_size,
				"red",
				stroke_points),
		}

		stroke_points = []
		posting = true;
		socket.send(make_header(args))
	})

	document.body.addEventListener("touchstart", function (e) {
	  if (e.target == draw) {
	    e.preventDefault();
	  }
	}, false);
	document.body.addEventListener("touchend", function (e) {
	  if (e.target == draw) {
	    e.preventDefault();
	  }
	}, false);
	document.body.addEventListener("touchmove", function (e) {
	  if (e.target == draw) {
	    e.preventDefault();
	  }
	}, false);

	$("#brush-size").on("input change", function (e) {
		$("#brush-size-text")[0].innerHTML = e.currentTarget.value
		stroke_size = e.currentTarget.value
	})
})

function findalllayer () {
	var n = 1;
	while (true) {
		var layer = document.getElementById("layer" + n);
		if (layer != undefined) {
			layers.push(layer);

			var ctx = layer.getContext("2d")
			ctx.strokeStyle = "red";
			ctx.lineWidth = "5";
			layer_ctxes.push(ctx);
		}
		else {
			break;
		}
		n ++;
	}
}

function undo () {
	args = {
		"method": PUT,
		"action": UNDO,
	}

	posting = true;
	socket.send(make_header(args))
}

function redo () {
	args = {
		"method": PUT,
		"action": REDO,
	}

	posting = true;
	socket.send(make_header(args))
}

function stroke_2_string (size, color, stroke) {
	string = format("{0},{1};",
		size,
		color)

	$.each(stroke, function (_, i) {
		string += i.join(",") + ";"
	})

	return string
}

function parse_storke_string (string) {
	info = string.split(";")
	info.pop()

	size = 5
	color = "red"
	points = []
	$.each(info, function (_, i) {
		if (_ == 0) {
			ele = i.split(",")
			size = ele[0]
			color = ele[1]
			return true;
		}
		pos = i.split(",")
		points.push([parseInt(pos[0]), parseInt(pos[1])])
	})

	stroke = {
		"size": size,
		"color": color,
		"points": points,
	}
	return stroke
}

function redraw () {
	$.each(layer_contains, function (i, stroke) {
		layer_ctxes[i].clearRect(0, 0, WIDTH, HEIGHT)
		if (stroke == undefined) {
			return true;
		}
		if (stroke["points"].length == 0) {
			return true;
		}
		layer_ctxes[i].strokeStyle = stroke["color"];
		layer_ctxes[i].lineWidth = stroke["size"];

		layer_ctxes[i].beginPath();
		layer_ctxes[i].moveTo(stroke["points"][0][0], stroke["points"][0][1]);

		for (e=1;e<stroke["points"].length;e++) {
			layer_ctxes[i].lineTo(stroke["points"][e][0], stroke["points"][e][1]);
		}
		layer_ctxes[i].stroke();
	})
}