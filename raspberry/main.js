const { io } = require("socket.io-client");
const path = require('path');
const { app, BrowserWindow } = require('electron')
const EventEmitter = require('events')
const loadingEvents = new EventEmitter()
const socket = io("http://192.168.2.12:8080");

const startWindow = () => new BrowserWindow({
    center: true,
    // titleBarStyle: 'hidden',
    webPreferences: {
        nodeIntegration: true
    },
    show: false
})

app.on('ready', () => {
    const mainWindow = startWindow()
    mainWindow.loadURL('https://meet.vku.udn.vn/son-18ce')
    mainWindow.once('ready-to-show', () => {
        mainWindow.show()
    })
})

socket.on("connect", () => {
    console.log('socket id: ', socket.id);
    socket.on('car_run', (msg) => {
        console.log(msg)
    })
});