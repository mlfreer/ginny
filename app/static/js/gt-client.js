var gaming = io.connect('http://' + document.domain + ':' + location.port + '/gaming');
var room_size = null
var moved = null
gaming.on('connected', function (data) {
    room_size = data['room_size']
    moved = data['moved']
});
gaming.on('started', function (data) {
    sleep(3000 + 500 * Math.random());
    location.reload()
});
gaming.on('moved', function (data) {
    moved += 1;
    if (moved == room_size) {
        sleep(300 * Math.random());
        location.reload();
    }
});
gaming.on('all_shown', function (data) {
    sleep(300 * Math.random());
    location.reload();
});
gaming.on('finished', function (data) {
    sleep(300 * Math.random());
    location.reload();
});
gaming.on('kicked', function (data) {
    sleep(300 * Math.random());
    location = data['redirect-url'];
});
function sleep(ms) {
    ms += new Date().getTime();
    while (new Date() < ms){}
}