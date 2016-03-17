<Recommend>
    <form onsubmit={submitRequest}>
        <div class="container-fluid m-t-1">
            <div class="row m-b-1">
                <div class="col-xs-12">
                    <span class="icon icon-title icon-lightbulb"></span>
                    <span class="title-display">Wikipedia</span>
                    <span class="title-display-strong">Suggestions</span>
                </div>
            </div>

            <div class="row m-b-1">
                <div class="col-xs-6 col-sm-4 col-md-3 col-lg-2 p-r-0">
                    <a type="button" class="btn btn-block btn-secondary source-selector" name="from">
                        <span class="selector-display">Source</span>
                        <span class="icon icon-selector icon-expand"></span>
                    </a>
                </div>
                <div class="col-xs-6 col-sm-4 col-md-3 col-lg-2 p-l-0">
                    <a type="button" class="btn btn-block btn-secondary target-selector" name="to">
                        <span class="selector-display">Target</span>
                        <span class="icon icon-selector icon-expand"></span>
                    </a>
                </div>
            </div>
        </div>
        <div class="container-fluid seed-container">
            <div class="row">
                <div class="col-xs-12">
                    <input type="text" class="form-control seed-input" placeholder="Seed article (optional)" name="seedArticle">
                </div>
            </div>
        </div>
    </form>
    <div class="container-fluid m-t-1">
        <div class="row">
            <div class="col-xs-12 col-md-10">
                <div class="text-xs-center alert alert-info" if={fetching}>
                    Preparing article recommendations...
                </div>
                <div class="text-xs-center alert alert-danger" if={error}>
                    {error_msg}
                </div>
            </div>
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
        self.sourceLanguages = {};
        self.targetLanguages = {};
        self.fetching = false;
        self.sourceSelector = null;
        self.targetSelector = null;
        self.uls = [];
        self.origin = 'unknown';

        self.submitRequest = function () {
            self.origin = 'form_submit';
            self.fetchArticles();
            return false;
        };

        self.fetchArticles = function () {
            if (!self.isInputValid()) {
                self.error = true;
                self.update();
                return;
            } else {
                self.error = false;
            }

            self.fetching = true;
            self.update();

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
                if (!articles || !articles.length) {
                    self.error_msg = articles['error'];
                    self.error = true;
                    self.update();
                } else {
                    riot.mount('articles', {
                        articles: articles,
                        source: self.source,
                        target: self.target
                    });
                }
            });
        };

        self.isInputValid = function () {
            if (self.source == self.target) {
                self.error_msg = "Source and target languages must be different";
                return false;
            } else if (!(self.source in self.sourceLanguages) || !(self.target in self.targetLanguages)){
                self.error_msg = "Invalid source or target language";
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

        self.setSource = function (code) {
            self.source = code;
            self.sourceSelector.find('.selector-display').text($.uls.data.getAutonym(self.source));
        };

        self.onSelectSource = function (code) {
            self.setSource(code);
            if (self.isInputValid()) {
                self.origin = 'language_select';
                self.fetchArticles();
            }
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
            self.targetSelector.find('.selector-display').text($.uls.data.getAutonym(self.target));
        };

        self.onSelectTarget = function (code) {
            self.setTarget(code);
            if (self.isInputValid()) {
                self.origin = 'language_select';
                self.fetchArticles();
            }
        };

        self.getTargetSelectorPosition = function () {
            var offset = self.targetSelector.offset();
            return {
                top: offset.top + self.targetSelector[0].offsetHeight,
                left: offset.left + self.targetSelector[0].offsetWidth - 360
            };
        };

        self.searchAPI = function (query) {
            var languageFilter = this;

            $.ajax({
                url: 'https://en.wikipedia.org/w/api.php',
                data: {
                    search: query,
                    format: 'json',
                    action: 'languagesearch'
                },
                dataType: 'jsonp',
                contentType: 'application/json'
            }).done(function (result) {
                $.each(result.languagesearch, function (code, name) {
                    if (languageFilter.resultCount === 0) {
                        languageFilter.autofill(code, name);
                    }
                    if (languageFilter.render(code)) {
                        languageFilter.resultCount++;
                    }
                });
                languageFilter.resultHandler(query);
            });
        };

        self.activateULS = function (selector, onSelect, getPosition, languages) {
            selector.uls({
                onSelect: onSelect,
                onReady: function () {
                    self.uls.push(this);
                    this.position = getPosition;
                },
                languages: languages,
                searchAPI: true, // this is set to true to simply trigger our hacky searchAPI
                compact: true,
                menuWidth: 'medium'
            });
        };

        self.on('mount', function () {
            // build language list with names from uls for the codes passed in to languagePairs
            window.translationAppGlobals.languagePairs['source'].forEach(function (code) {
                self.sourceLanguages[code] = $.uls.data.getAutonym(code);
            });
            window.translationAppGlobals.languagePairs['target'].forEach(function (code) {
                self.targetLanguages[code] = $.uls.data.getAutonym(code);
            });

            // Use a more flushed out ajax call to wikipedia's api
            // Otherwise, CORS stops the request
            $.fn.languagefilter.Constructor.prototype.searchAPI = self.searchAPI;

            // build the selectors using the language lists
            self.sourceSelector = $('a[name=from]');
            self.targetSelector = $('a[name=to]');
            self.activateULS(self.sourceSelector, self.onSelectSource, self.getSourceSelectorPosition, self.sourceLanguages);
            self.activateULS(self.targetSelector, self.onSelectTarget, self.getTargetSelectorPosition, self.targetLanguages);

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

            self.populateDefaults(self.sourceLanguages, self.targetLanguages);

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
