const mosca = require('mosca');
const io = require('socket.io')(8080, {
    cors: {
        methods: ["GET", "POST"]
    }
});
const settings = {
    interfaces: [
        { type: "mqtt", port: 1883 },
    ]
};

const broker = new mosca.Server(settings);

broker.on('ready', setup);

io.on('connection', socket => {
    console.log('WS Connect: ' + socket.id);
    socket.onAny((topic, msg) => {
        console.log('response.topic: ' + topic)
        console.log('response.body: ' + msg)
        broker.publish({
            topic: topic,
            payload: msg
        })
    });
    socket.on('disconnect', () => {
        console.log('WS Disconnect: ', socket.id);
    })
});

broker.on('clientConnected', function (client) {
    console.log('client Mqtt connected:        ', client.id);
});

broker.on('published', (msg) => {
    console.log('response.topic: ' + msg.topic)
    console.log('response.body: ' + msg.payload.toString())
    io.emit(msg.topic, msg.payload.toString());
});


broker.on('clientDisconnected', (client) => {
    console.log('client Mqtt Disconnected:      ', client.id);
});

function setup() {
    console.log('Mosca server is up and running');
}
