$('.hide-ok').click(function (e) {
    e.preventDefault();
    $('.panel.panel-success').parent('div').hide();
});

$('.show-ok').click(function (e) {
    e.preventDefault();
    $('.panel.panel-success').parent('div').show();
});
