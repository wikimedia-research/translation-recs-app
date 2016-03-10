<Recommend>
    <div class="jumbotron jumbotron-fluid">
        <div class="container">
            <div class="row m-b-1 text-xs-center">
                <h2>Wikipedia Translation Recommendation</h2>
                <p>Select a language pair and seed article</p>
            </div>
            <form>
                <div class="row m-b-1">
                    <div class="col-xs-6 col-sm-5 col-sm-offset-1 col-md-4 col-md-offset-2 p-r-0">
                        <input type="button" class="btn btn-block btn-secondary" name="from" value="Source">
                    </div>
                    <div class="col-xs-6 col-sm-5 col-md-4 p-l-0">
                        <input type="button" class="btn btn-block btn-secondary target-selector" name="to" value="Target">
                    </div>
                </div>
                <div class="row">
                    <div class="col-xs-12 col-sm-10 col-sm-offset-1 col-md-8 col-md-offset-2 input-group">
                        <input type="text" class="form-control" placeholder="Seed article (optional)" name="seedArticle">
                        <span class="input-group-btn">
                            <button type="button" class="btn btn-secondary" onclick={submitRequest}>
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
        <div class={invisible: fetching || error}>
            <articles></articles>
        </div>
    </div>

    <preview></preview>

    <script>
        var self = this;

        self.source = '';
        self.target = '';
        self.fetching = false;
        self.sourceSelector = null;
        self.targetSelector = null;
        self.uls = [];
        self.origin = 'unknown';

        self.submitRequest = function () {
            self.origin = 'form_submit';
            self.fetchArticles();
        };

        self.fetchArticles = function () {
            if (!self.isInputValid()) {
                return;
            }

            self.fetching = true;

            var url = '/api?s=' + self.source + '&t=' + self.target;

            var seed;
            if (this.seedArticle.value) {
                url += '&article=' + encodeURIComponent(this.seedArticle.value);
                seed = this.seedArticle.value;
            }

            logUIRequest(self.source, self.target, seed, self.origin);

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
            } else {
                self.error = false;
            }
            return !self.error;
        };

        self.filter = function (articles) {
            var personalBlacklist = store(translationAppGlobals.personalBlacklistKey) || {},
                targetWikiBlacklist = (store(translationAppGlobals.globalBlacklistKey) || {})[self.target.value] || {};

            return articles.filter(function (a) {
                return !personalBlacklist.hasOwnProperty(a.wikidata_id)
                    && !targetWikiBlacklist.hasOwnProperty(a.wikidata_id);
            });
        };

        self.setSource = function (code) {
            self.source = code;
            self.sourceSelector.val($.uls.data.getAutonym(self.source));
        };

        self.getSourceSelectorPosition = function () {
            var offset = self.sourceSelector.offset();
            return {
                top: offset.top + self.sourceSelector[0].offsetHeight,
                left: offset.left
            };
        };

        self.setTarget = function (code) {
            self.target = code;
            self.targetSelector.val($.uls.data.getAutonym(self.target));
        };

        self.getTargetSelectorPosition = function () {
            var offset = self.targetSelector.offset();
            return {
                top: offset.top + self.targetSelector[0].offsetHeight,
                left: offset.left + self.targetSelector[0].offsetWidth - 360
            };
        };

        self.activateULS = function (selector, onSelect, getPosition, languages) {
            selector.uls({
                onSelect: onSelect,
                onReady: function () {
                    self.uls.push(this);
                    this.position = getPosition;
                },
                languages: languages,
                compact: true,
                menuWidth: 'medium'
            });
        };

        self.on('mount', function () {
            // build language list with names from uls for the codes passed in to languagePairs
            var sourceLanguages = {};
            var targetLanguages = {};
            window.translationAppGlobals.languagePairs['source'].forEach(function (code) {
                sourceLanguages[code] = $.uls.data.getAutonym(code);
            });
            window.translationAppGlobals.languagePairs['target'].forEach(function (code) {
                targetLanguages[code] = $.uls.data.getAutonym(code);
            });

            // build the selectors using the language lists
            self.sourceSelector = $('input[name=from]');
            self.targetSelector = $('input[name=to]');
            self.activateULS(self.sourceSelector, self.setSource, self.getSourceSelectorPosition, sourceLanguages);
            self.activateULS(self.targetSelector, self.setTarget, self.getTargetSelectorPosition, targetLanguages);

            // hide the selectors if the window resizes with a timeout
            var resizeTimer;
            $(window).resize(function () {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(function () {
                    $.each(self.uls, function (index, item) {
                        item.hide();
                    });
                }, 50);
            });

            self.populateDefaults(sourceLanguages, targetLanguages);

            if (self.source && self.target) {
                self.fetchArticles();
            }
        });

        self.populateDefaults = function (sourceLanguages, targetLanguages) {
            if (window.translationAppGlobals.s in sourceLanguages) {
                self.setSource(window.translationAppGlobals.s);
                self.origin = 'url_parameters';
            }
            if (window.translationAppGlobals.t in targetLanguages) {
                self.setTarget(window.translationAppGlobals.t);
                self.origin = 'url_parameters';
            }

            var browserLanguages = navigator.languages || [ navigator.language || navigator.userLanguage ];
            browserLanguages = browserLanguages.filter(function (language) {
                return language in sourceLanguages;
            });

            if (!self.source) {
                var index = Math.floor(Math.random() * browserLanguages.length);
                self.setSource(browserLanguages[index]);
                self.origin = 'browser_settings';
                // remove option from the list of languages
                // this is not exactly the desired behavior, since the list is filtered based on the sourceLanguages
                // and this leaves the possibility for a populated target language to not be valid; however, since
                // currently the source and target language lists are the same, this works
                // TODO: remove hack described above
                browserLanguages.splice(index, 1);
            }
            if (!self.target) {
                if (browserLanguages.length) {
                    self.setTarget(browserLanguages[Math.floor(Math.random() * browserLanguages.length)]);
                    self.origin = 'browser_settings';
                }
            }

            $('input[name=seedArticle]').val(window.translationAppGlobals.seed);
        };

    </script>
</Recommend>
