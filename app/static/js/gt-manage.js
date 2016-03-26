var gaming_manage = io.connect('http://' + document.domain + ':' + location.port + '/gaming_manage');
gaming_manage.on('gamer_register', function (data) {
    $('#gamer-count').text(parseInt($('#gamer-count').text()) + 1)
    $('#gamers').append("<span id='gamer_badge_" + data['id'] + "' class='label label-primary spacer-right-1'>Gamer "
        + data['id'] +
        "<span class='spacer-left-1' onclick='return confirm(\"Are you sure?\")' data-href='" + data['url'] + "'>⨉</span>")
    $("[data-href]").css('cursor','pointer');
    $("[data-href]").click(function() {
        window.document.location = $(this).data("href");
    });
});
gaming_manage.on('new_round', function (data) {
    location.reload()
});
gaming_manage.on('gamer_unregister', function (data) {
    $('#gamer-count').text(parseInt($('#gamer-count').text()) - 1)
    $('#gamer_badge_' + data['id']).remove()
});
gaming_manage.on('connected', function (data) {
    gaming_manage.emit("tell_game_trial_id", {'game_trial_id': $('#gamer_trial_id').text()})
});