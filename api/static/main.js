'use strict';

var items = [
    { view: 'Recommend' },
    { view: 'About' },
];

riot.mount('menu', { items: items });

var page = document.getElementById('page');

riot.route(function (view, seedArticle) {
    var custom = document.createElement(view);
    page.innerHTML = '';
    page.appendChild(custom);

    riot.mount(page, view, { seedArticle: seedArticle });
});
riot.route.start();
riot.route('Recommend');
