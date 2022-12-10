const { io } = require("socket.io-client");
const socket = io("http://localhost:8080");
let count = 0 
socket.on("connect", () => {
    console.log('socket id: ', socket.id);
    setInterval(() => {
        socket.emit('car_run',count++)
    }, 100)
});