<preview class="ui modal preview">

    <div class="ui three quarters scrollable container">
        <h2 class="ui header">{ title }</h2>
        <div class="preview body"></div>
    </div>
    <div class="ui menu">
        <div class="item">
            <button class="ui button">
                <i class="remove icon"></i>
                Skip
            </button>
        </div>
        <div class="item">
            <button class={
                disabled: showIndex === 0,
                ui: true, icon: true, button: true
            } onclick={ left }>
                <i class="grey chevron left icon"></i>
            </button>
        </div>
        <div class="item">
            <button class={
                disabled: showIndex > (articles.length - 2),
                ui: true, icon: true, button: true
            } onclick={ right }>
                <i class="grey chevron right icon"></i>
            </button>
        </div>
        <div class="right menu">
            <div class="item">
                <a class="ui primary translate button" target="_blank"
                   href={ translateLink }>
                    <i class="write icon"></i>
                    Translate
                </a>
            </div>
        </div>
    </div>

    <script>
        var self = this;

        self.articles = opts.articles || [];
        self.title = opts.title || '';
        // TODO: should this link to the destination wiki?
        self.translateRoot = '//en.wikipedia.org/wiki/Special:ContentTranslation?' +
            'from=' + opts.from +
            '&to=' + opts.to +
            '&campaign=article-recommendation';

        self.index = -1;
        for (var i=0; i<self.articles.length; i++) {
            if (self.articles[i].title === self.title) {
                self.showIndex = i;
                break;
            }
        }

        var mobileRoot = 'http://rest.wikimedia.org/en.wikipedia.org/v1/page/html/';

        self.show = function () {
            var showing = self.articles[self.showIndex];
            self.title = showing.title;
            self.translateLink = self.translateRoot + '&page=' + showing.linkTitle;

            $('.preview.body').append('<div class="mask">Loading...</div>');

            $.get(mobileRoot + showing.title).done(function (data) {;
                self.showPreview(showing, data);
            }).fail(function (data) {
                self.showPreview(showing, 'No Internet');
            });
        }

        self.showPreview = function (showing, body) {
            $('.preview.body').html(body);

            $('.ui.modal.preview').modal({
                onHide: function () {
                    // strip out the nasty CSS
                    $('.preview.body').html('');
                },
            }).modal('show');

            self.update();
        }

        left (e) {
            if (self.showIndex > 0) {
                self.showIndex --;
                self.show();
            }
        }

        right (e) {
            if (self.showIndex < self.articles.length - 1) {
                self.showIndex ++;
                self.show();
            }
        }

        if (isFinite(self.showIndex)) {
            self.show();
        }

        /*
        this.on('mount', function () {
            var showing = self.articles[self.showIndex];
            if (!showing) { return; }

            $('.preview a.translate.button')[0].href =
                self.translateRoot + '&page=' + showing.linkTitle;
        });
        */
    </script>

</preview>
