$('.hide-ok').click(function (e) {
    e.preventDefault();
    $('.card.card-outline-success').parent('div').hide();
});

$('.show-ok').click(function (e) {
    e.preventDefault();
    $('.card.card-outline-success').parent('div').show();
});

$(document).ready(function () {
    $('[data-toggle="tooltip"]').tooltip()
});
