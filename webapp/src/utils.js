const { io } = require("socket.io-client");

var socket = null;

export function socketConnect(gameId) {
    if (socket === null) {
        socket = io("http://localhost:5000");
        socket.on('connect', () => {
            socket.emit("join", {gameId: gameId});
        });
    }
    return socket;
}


async function request(method, uri, data={}, callback=function() {}) {
    let body = ["get", "head"].includes(method.toLowerCase()) ? null : JSON.stringify(data);
    await fetch(uri, {
        method: method,
        mode: "cors",
        headers: {
          'Content-Type': 'application/json'
        },
        redirect: 'follow',
        body: body
    }).then(response => response.json())
    .then(callback)
    .catch(error => {
        console.log(error);
    });
}

export async function post(uri, data, callback=function() {}) {
    return request("POST", uri, data, callback);
}

export async function get(uri, callback=function() {}) {
    return request("GET", uri, {}, callback);
}
