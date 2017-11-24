function newBoard () {
	$("#blackscreen").show()
	$("#alert").show()
	$("#createing-board").show()

	try {
		socket = new WebSocket("ws://" + window.location.hostname + ":21085")
	} catch (e) {
		alert("Cannot connect to server, please try again later.")
	}

	socket.onmessage = function (e) {
		args = parse(e.data)
		
		if (args["method"] == "NEWBOARD") {
			if (args["success"] == "True") {
				window.location.pathname = "/draw/" + args["board_id"]
			}
			else {
				$("#createing-board").hide()
				$("#no-room").show()

				setTimeout(function () {
					$("#blackscreen").hide(300)
					$("#alert").hide(300)
					$("#no-room").hide(300)
				}, 5000)
			}
		}
	}

	socket.onopen = function () {
		args = {
			"method": "NEWBOARD",
		}
		socket.send(make_header(args))
	}
}