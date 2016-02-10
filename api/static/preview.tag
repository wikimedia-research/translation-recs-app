<preview class="ui modal preview">

    <div class="ui three quarters scrollable container">
        <h2 class="ui header">{ title }</h2>
        <div class="preview body"></div>
    </div>
    <div class="ui menu">
        <div class="item">
            <button class="ui top right corner icon button pointing personalize dropdown link">
                <i class="flag icon"></i>
                <div class="menu">
                    <div class="item" onclick={ addToPersonalBlacklist }>
                        Remove, I am not interested
                    </div>
                    <div class="item" onclick={ addToGlobalBlacklist }>
                        Remove, this is not notable for { opts.to } wikipedia
                    </div>
                </div>
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
                <div class="ui teal buttons">
                    <a class="ui primary translate button" target="_blank"
                       href={ translateLink }>
                    <i class="write icon"></i>
                       Translate
                    </a>
                    <div class="ui dropdown icon button">
                       <i class="dropdown icon"></i>
                       <div class="menu">
                           <div class="item">
                               <i class="unhide icon"></i><a target="_blank"
                                    href={ articleLink }>
                               View article
                               </a>
                            </div>
                       </div>
                    </div>
		</div>
            </div>
        </div>
    </div>

    <script>
        var self = this;

        self.articles = opts.articles || [];
        self.title = opts.title || '';
        self.translateRoot = '//' + opts.from + '.wikipedia.org/wiki/Special:ContentTranslation?' +
            'from=' + opts.from +
            '&to=' + opts.to +
            '&campaign=' + translationAppGlobals.campaign;

        self.articleRoot = '//' + opts.from + '.wikipedia.org/wiki/';

        self.index = -1;
        for (var i=0; i<self.articles.length; i++) {
            if (self.articles[i].title === self.title) {
                self.showIndex = i;
                break;
            }
        }

        var previewRoot = 'https://rest.wikimedia.org/' + opts.from + '.wikipedia.org/v1/page/html/';

        self.show = function () {
            var showing = self.articles[self.showIndex];
            self.title = showing.title;
            self.translateLink = self.translateRoot + '&page=' + showing.linkTitle;
            self.articleLink = self.articleRoot + showing.linkTitle;

            $.get(previewRoot + showing.title).done(function (data) {
                self.showPreview(showing, data);
            }).fail(function (data) {
                self.showPreview(showing, 'No Internet');
            });
        };

        self.showPreview = function (showing, body) {
            $('.preview.body', self.root).html(body);

            $(self.root).modal({
                onHide: function () {
                    // strip out the nasty CSS
                    $('.preview.body', self.root).html('');
                },
            }).modal('show');

            // enable any dropdown
            $('.ui.dropdown', self.root).dropdown();

            self.update();
        };

        addToPersonalBlacklist () {
            opts.remove(self.articles[self.showIndex], true);
            $(self.root).modal('hide');
        }

        addToGlobalBlacklist () {
            opts.remove(self.articles[self.showIndex], false);
            $(self.root).modal('hide');
        }

        left () {
            if (self.showIndex > 0) {
                self.showIndex --;
                self.show();
            }
        }

        right () {
            if (self.showIndex < self.articles.length - 1) {
                self.showIndex ++;
                self.show();
            }
        }

        if (isFinite(self.showIndex)) {
            self.show();
        }
    </script>

</preview>
