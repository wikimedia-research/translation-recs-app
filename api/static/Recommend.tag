<Recommend>
    <form onsubmit={submitRequest}>
        <div class="container-fluid m-t-1">
            <div class="row m-b-1">
                <div class="dropdown">
                    <div class="col-xs-12">
                        <span class="icon icon-title icon-lightbulb"></span>
                        <span class="title-display">Wikipedia</span>
                        <span class="title-display-strong">GapFinder</span>
                        <span class="icon icon-title icon-menu dropdown-toggle"
                              data-toggle="dropdown"></span>
                        <div class="dropdown-menu dropdown-menu-right">
                            <button class="dropdown-item" type="button"
                                    data-toggle="modal" data-target="#howToModal">How to</button>
                            <button class="dropdown-item" type="button"
                                    data-toggle="modal" data-target="#aboutModal">About</button>
                        </div>
                    </div>
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
            <div class="col-xs-12 col-sm-8 col-md-6 col-lg-4">
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

    <div id="howToModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal">
                        <h4 class="modal-title">&#x274c;</h4>
                    </button>
                    <h4 class="modal-title">How to</h4>
                </div>
                <div class="modal-body">
                    GapFinder helps you discover articles that exist one language but are missing another.

                    Start by selecting a source language and a target language. GapFinder will find trending articles in the source that  are missing in the target. 

                    If you are interested in a particular topic area, provide a seed article in the source language, and GapFinder will find related articles missing in the target.

                    Click on a card to take a closer look at a missing article to see if you would like to create it from scratch or translate it.

                </div>
            </div>
        </div>
    </div>

    <div id="aboutModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal">
                        <h4 class="modal-title">&#x274c;</h4>
                    </button>
                    <h4 class="modal-title">About</h4>
                </div>
                <div class="modal-body">

                We are a team of researchers and developers in the Wikimedia Foundation and Stanford University interested in identifying gaps of knowledge across the more than 160 active language editions of Wikipedia. <br><br>

                Back in 2015, we started a project to identify missing content in Wikipedia, rank it by its importance, and recommend the ranked missing content to Wikipedia’s volunteer editors based on their interests as captured by their editor history. We ran an experiment in June 2015 in French Wikipedia where we showed that by emailing recommendations to volunteer editors we can triple the article creation rate in Wikipedia while maintaining the current level of quality in Wikipedia articles. If you are interested to learn more about that research, you can read more about it <a href = "http://arxiv.org/abs/1604.03235"> here</a>.<br><br>

                Encouraged by the result of the experiment, we have developed Wikipedia GapFinder, an app that helps you find missing content in any language for which there is a Wikipedia edition. GapFinder can help you to easily find articles to create in the language of your choice. It also lets you personalize the recommendations by providing a seed article, an article that you would like to receive similar missing article recommendations. <br><br>

                GapFinder is a research app at the moment. By using it, you will make more content available in your local language, and help us understand how we can improve the app. <br><br>


                <h6>In the media: </h6>
                <a href = "http://www.lemonde.fr/sciences/article/2016/01/11/wikipedia-la-connaissance-en-mutation_4845347_1650684.html"> Le Monde: Wikipédia, quinze ans de recherches </a>
                </div>
            </div>
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
            self.origin = 'language_select';
            self.fetchArticles();
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
            self.origin = 'language_select';
            self.fetchArticles();
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
