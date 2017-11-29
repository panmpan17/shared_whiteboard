published_get = false

function newBoard () {
	$("#blackscreen").show()
	$("#alert").show()
	$("#createing-board").show()

	try {
		socket = new WebSocket(socket_ip)
	} catch (e) {
		$("#createing-board").hide()
		$("#bad-connection").show()

		setTimeout(function () {
			$("#blackscreen").hide(300)
			$("#alert").hide(300)
			$("#bad-connection").hide(300)
		}, 3000)
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
				}, 3000)
			}
		}
	}

	socket.onopen = function () {
		args = {
			"method": "NEWBOARD",
		}
		socket.send(make_header(args))
	}

	socket.onclose = function () {
		$("#createing-board").hide()
		$("#bad-connection").show()

		setTimeout(function () {
			$("#blackscreen").hide(300)
			$("#alert").hide(300)
			$("#bad-connection").hide(300)
		}, 3000)
	}
}

function showContact () {
	$("#blackscreen").show()
	$("#page").show()
	$("#contact-report").show()
}

function showAbout (){
	$("#blackscreen").show()
	$("#page").show()
	$("#aboute-website").show()
}

function showPublished (){
	$("#blackscreen").show()
	$("#page").show()
	$("#published-board").show()

	if (!published_get) {
		$.ajax({
			url: host + "board/",
			success: function (msg) {
				published_get = true;
				$.each(msg, function (_, board) {
					console.log(board)
					$("#published-board")[0].innerHTML += format(
						`<img src="{0}">`,
						board["base64"],
						)
				})
			}
		})
	}
}

function hidePage () {
	$("#blackscreen").hide()
	$("#page").hide()
	$("#contact-report").hide()
	$("#aboute-website").hide()
	$("#published-board").hide()
}

function submitContact () {
	nickname = $("#nickname")[0].value
	email = $("#email")[0].value
	content = $("#content")[0].value

	if ((nickname == "") || (email == "") || (content == "")) {
		alert("Please don't leave blank");
		return;
	}

	json = {
		"nickname": nickname,
		"email": email,
		"content": content,
	}

	$.ajax({
		url: host + "report/",
		type: "POST",
		dataType: "json",
		data: JSON.stringify(json),
		contentType: "application/json; charset=utf-8",
		success: function (msg) {
			$("#contact-report").hide()
			$("#page").hide()

			$("#alert").show()
			$("#thanks").show()

			setTimeout(function () {
				$("#blackscreen").hide(300)
				$("#alert").hide(300)
				$("#thank").hide(300)
			}, 3000)
		}
	})
}