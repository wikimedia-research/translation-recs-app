<Recommend>
    <div class="jumbotron jumbotron-fluid">
        <div class="container">
            <div class="row m-b-1 text-xs-center">
                <h2>Wikipedia Translation Recommendation</h2>
                <p>Select a language pair and seed article</p>
            </div>
            <form>
                <div class="row m-b-1">
                    <div class="col-xs-6 col-sm-4 col-sm-offset-2 col-md-3 col-md-offset-3">
                        <input type="button" class="btn btn-secondary btn-block" name="from" value="Source">
                    </div>
                    <div class="col-xs-6 col-sm-4 col-md-3">
                        <input type="button" class="btn btn-secondary btn-block" name="to" value="Target">
                    </div>
                </div>
                <div class="row m-b-3">
                    <div class="col-sm-10 col-sm-offset-1 col-md-6 col-md-offset-3 input-group">
                        <input type="text" class="form-control form-control" placeholder="Seed article (optional)" name="seedArticle">
                        <span class="input-group-btn">
                            <button type="submit" class="btn btn-secondary" onclick={fetchArticles}>
                                Recommend
                            </button>
                        </span>
                    </div>
                </div>
            </form>
        </div>
    </div>
    <div class="container">
        <div class="text-xs-center" if={fetching}>
            Preparing article recommendations...
        </div>
        <div class="text-xs-center alert alert-danger" role="alert" if={error}>
            {error_msg}
        </div>
        <div class={invisible: fetching || starting || error}>
            <articles></articles>
        </div>
    </div>

    <preview></preview>

    <script>
        var self = this;

        self.languagePairs = window.translationAppGlobals.languagePairs;
        self.sources = self.languagePairs['source'].sort();
        self.targets = self.languagePairs['target'].sort();
        self.defaultSource = window.translationAppGlobals.s;
        self.defaultTarget = window.translationAppGlobals.t;
        self.defaultSeed = window.translationAppGlobals.seed;
        self.source = self.defaultSource || '';
        self.target = self.defaultTarget || '';
        self.fetching = false;
        self.starting = true;

        self.fetchArticles = function () {
            if (!self.isInputValid()) {
                return;
            }

            self.error = false;
            self.starting = false;
            self.fetching = true;
            self.update();

            var url = '/api?s=' + self.source + '&t=' + self.target;

            var seed;
            if (this.seedArticle.value) {
                url += '&article=' + encodeURIComponent(this.seedArticle.value);
                seed = this.seedArticle.value;
            }

            logUIRequest(self.source, self.target, seed);

            $.ajax({
                url: url
            }).complete(function () {
                self.fetching = false;
                self.update();
            }).done(function (data) {
                if (data.error) {
                    self.error = true;
                    self.error_msg = data.error;
                    return;
                }

                var articles = self.filter(data.articles);

                riot.mount('articles', {
                    articles: articles,
                    source: self.source,
                    target: self.target
                });
            });
        };

        self.isInputValid = function () {
            if (self.source == self.target) {
                self.error_msg = "Source and target languages must be different";
                self.error = true;
                return false;
            }
            return true;
        };

        self.filter = function (articles) {
            var personalBlacklist = store(translationAppGlobals.personalBlacklistKey) || {},
                targetWikiBlacklist = (store(translationAppGlobals.globalBlacklistKey) || {})[self.target.value] || {};

            return articles.filter(function (a) {
                return !personalBlacklist.hasOwnProperty(a.wikidata_id)
                    && !targetWikiBlacklist.hasOwnProperty(a.wikidata_id);
            });
        };

        self.on('mount', function () {
            var sourceSelector = $('input[name=from]');
            var targetSelector = $('input[name=to]');
            var uls = [];

            sourceSelector.uls({
                onSelect: function(language) {
                    self.source = language;
                    var languageName = $.uls.data.getAutonym(language);
                    sourceSelector.val(languageName);
                },
                onReady: function() {
                    uls.push(this);
                    this.position = function () {
                        var offset = sourceSelector.offset();
                        return {
                            top: offset.top + sourceSelector[0].offsetHeight,
                            left: offset.left
                        };
                    };
                },
                compact: true,
                menuWidth: 'medium'
            });

            targetSelector.uls({
                onSelect: function(language) {
                    self.target = language;
                    var languageName = $.uls.data.getAutonym(language);
                    targetSelector.val(languageName);
                },
                onReady: function() {
                    uls.push(this);
                    this.position = function () {
                        var offset = targetSelector.offset();
                        return {
                            top: offset.top + targetSelector[0].offsetHeight,
                            left: offset.left + targetSelector[0].offsetWidth - 360
                        };
                    };
                },
                compact: true,
                menuWidth: 'medium'
            });

            var resizeTimer;
            $(window).resize(function() {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(function () {
                    $.each(uls, function (index, item) {
                        item.hide();
                    });
                }, 50);
            });

            if (self.source) {
                sourceSelector.val($.uls.data.getAutonym(self.source));
            }
            if (self.target) {
                targetSelector.val($.uls.data.getAutonym(self.target));
            }
            $('input[name=seedArticle]').val(self.defaultSeed);
            if (self.source && self.target) {
                self.fetchArticles();
            }
            self.update();
        });

    </script>
</Recommend>
