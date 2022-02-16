var net = require('net');

function SkyRemote(host, port) {

	var that = this;
	this.connectTimeout = 1000;

	function sendCommand(code, cb) {
		var commandBytes = [4,1,0,0,0,0, Math.floor(224 + (code/16)), code % 16];

		var client = net.connect({
			host: host,
			port: port || 49160
		});

		var l = 12;
		client.on('data', function(data) {
			clearTimeout(connectTimeoutTimer)
			// Clear timeout
			if (data.length < 24) {
				client.write(data.slice(0, l))
				l = 1;
			} else {
				client.write(new Buffer(commandBytes), function() {
					commandBytes[1]=0;
					client.write(new Buffer(commandBytes), function() {
						client.destroy();
						cb(null)
					});
				});
			}
		});

		client.on('error', function(err) {
			clearTimeout(connectTimeoutTimer)
			cb(err)
		})

		var connectTimeoutTimer = setTimeout(function() {
			client.end()
			var err = new Error('connect timeout '+host+':'+port)
			err.name = 'ECONNTIMEOUT'
			err.address = host
			err.port = port
			cb(err)
		}, that.connectTimeout)
	}

	this.press = function press(sequence, cb) {
		if (typeof sequence !== 'object' || !sequence.hasOwnProperty('length')) {
			return press(sequence.split(','), cb)
		};
		sendCommand(SkyRemote.commands[sequence.shift()],function(err) {
			if (sequence.length) {
				setTimeout(function() {
					press(sequence, cb);
				},500);
			} else {
				if (typeof cb === 'function') {
					cb(err);
				}
			}
		});
	}

}

SkyRemote.SKY_Q_LEGACY = 5900;
SkyRemote.SKY_Q = 49160;