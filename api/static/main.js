'use strict';

var page = document.getElementById('page');

riot.route(function (view) {
    var custom = document.createElement(view);
    page.innerHTML = '';
    page.appendChild(custom);

    riot.mount(page, view);
});
riot.route.start();
riot.route('Recommend');
