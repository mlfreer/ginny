$(document).ready(function() {
    if (location.hash !== '') $('a[href="' + location.hash + '"]').tab('show');
    $('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
      return location.hash = $(e.target).attr('href').substr(1);
    });
    $("[data-href]").css('cursor','pointer');
    $("[data-href]").click(function() {
        window.document.location = $(this).data("href");
    });
    $('[data-toogle="tooltip"]').tooltip();
    $('[name="tz"]').val(new Date().getTimezoneOffset())
    $('.moment-time-text').text(function(){
        return moment.utc($(this).text()).local().format("MM/DD/YYYY hh:mm A")
    })
    $('.moment-time-val').attr('value', function(){
        return moment.utc($(this).attr('value')).local().format("MM/DD/YYYY hh:mm A")
    })
    $('.datetimepicker').datetimepicker({});
    $("textarea").keydown(function(e) {
    if(e.keyCode === 9) { // tab was pressed
        // get caret position/selection
        var start = this.selectionStart;
        var end = this.selectionEnd;

        var $this = $(this);
        var value = $this.val();

        // set textarea value to: text before caret + tab + text after caret
        $this.val(value.substring(0, start)
                    + "\t"
                    + value.substring(end));

        // put caret at right position again (add one for the tab)
        this.selectionStart = this.selectionEnd = start + 1;

        // prevent the focus lose
        e.preventDefault();
    }
});
});
