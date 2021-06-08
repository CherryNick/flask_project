var socket = io();
socket.on('connect', () => {
    socket.emit('user_connect', '{{current_user.id}}');
});

socket.emit('send_from', 'data', '10');

// socket.on('send_private_message', data)
socket.on("send_to", (data) => {
    console.log(data['data']);
    console.log(data['from_id']);
});
// handle the event sent with socket.send()
socket.on("message", data => {
    console.log(data);
});