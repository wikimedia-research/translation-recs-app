<gf-input>
    <form onsubmit={submitRequest}>
        <div class="gf-selector-container">
            <a class="btn btn-secondary gf-selector-source" name="from">
                <div class="gf-selector-button-container">
                    <span class="gf-selector-text">{$.i18n('selector-source')}</span>
                    <span class="gf-icon gf-icon-expand"></span>
                </div>
            </a>
            <a class="btn btn-secondary gf-selector-target" name="to">
                <div class="gf-selector-button-container">
                    <span class="gf-selector-text">{$.i18n('selector-target')}</span>
                    <span class="gf-icon gf-icon-expand"></span>
                </div>
            </a>
        </div>
        <div class="gf-seed-container" id="seed-container">
            <span class="gf-icon gf-icon-search gf-seed-icon"></span>
            <input type="text" autocomplete=off class="gf-seed-input"
                   placeholder={ $.i18n('search-placeholder') } name="seedArticle">
        </div>
    </form>
    <div class="gf-input-status-container" if={fetching || error}>
        <div class="gf-input-status alert alert-info" data-i18n="status-preparing" if={fetching}>
            {$.i18n('status-preparing')}
        </div>
        <div class="gf-input-status alert alert-danger" data-i18n="{error_msg}" if={error}>
            {$.i18n(error_msg)}
        </div>
    </div>
    <div class={invisible: fetching || error}>
        <gf-articles></gf-articles>
    </div>

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
        self.currentMenuWidth = '';

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

            var mappedSource = self.mapLanguageToDomainCode(self.source);
            var mappedTarget = self.mapLanguageToDomainCode(self.target);
            var url = '/api/?s=' + mappedSource + '&t=' + mappedTarget;

            var seed;
            if (this.seedArticle.value) {
                url += '&article=' + encodeURIComponent(this.seedArticle.value);
                seed = this.seedArticle.value;
            }

            logUIRequest(mappedSource, mappedTarget, seed, self.origin);

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
                    riot.mount('gf-articles', {
                        articles: articles,
                        source: mappedSource,
                        target: mappedTarget
                    });
                }
            });
        };

        self.mapLanguageToDomainCode = function (language) {
            return translationAppGlobals.languageToDomainMapping[language] || language;
        };

        self.isInputValid = function () {
            if (self.source == self.target) {
                self.error_msg = 'status-must-be-different';
                return false;
            } else if (!(self.source in self.sourceLanguages) || !(self.target in self.targetLanguages)){
                self.error_msg = 'status-invalid-language';
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
            updateLanguage(self.source);
            self.sourceSelector.find('.gf-selector-text').text($.uls.data.getAutonym(self.source));
        };

        self.onSelectSource = function (code) {
            self.setSource(code);
            self.origin = 'language_select';
            $('input[name=seedArticle]').val('');
            if (self.target) {
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
            self.targetSelector.find('.gf-selector-text').text($.uls.data.getAutonym(self.target));
        };

        self.onSelectTarget = function (code) {
            self.setTarget(code);
            self.origin = 'language_select';
            self.fetchArticles();
        };

        self.getTargetSelectorPosition = function () {
            var offset = self.targetSelector.offset();
            var top = offset.top + self.targetSelector[0].offsetHeight;
            var minMediumColWidth = 360;
            var left = offset.left + self.targetSelector[0].offsetWidth - minMediumColWidth;
            if (self.getMenuWidth() === 'narrow') {
                var minNarrowColWidth = 180;
                left = offset.left + self.targetSelector[0].offsetWidth - minNarrowColWidth;
            }
            return {
                top: top,
                left: left
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

        self.getMenuWidth = function () {
            var smallestWidthForMedium = 390;
            if ($(window).width() < smallestWidthForMedium) {
                return 'narrow';
            } else {
                return 'medium';
            }
        };

        self.activateULS = function (selector, onSelect, getPosition, languages) {
            selector.uls({
                onSelect: onSelect,
                onReady: function () {
                    self.uls.push(this);
                    this.position = getPosition;
                },
                onVisible: function() {
                    this.i18n();
                },
                languages: languages,
                searchAPI: true // this is set to true to simply trigger our hacky searchAPI
            });
            self.currentMenuWidth = self.getMenuWidth();
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

            // Have a dynamic menu width based on screen size
            $.fn.uls.Constructor.prototype.getMenuWidth = self.getMenuWidth;

            // Disable scroll into view added by ULS
            $.fn.scrollIntoView = function () {};

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
                    if (self.currentMenuWidth !== self.getMenuWidth()) {
                        // destroy and re-initialize the language dropdown
                        // to accommodate changing from the 'medium' to 'narrow' menuWidth
                        $.each(self.uls, function (index, item) {
                            item.show(); // ensure uls is initialized before it's destroyed
                            item.hide();
                            item.$menu.remove();
                        });
                        $.removeData(self.sourceSelector.get(0));
                        $.removeData(self.targetSelector.get(0));
                        self.sourceSelector.off('uls');
                        self.targetSelector.off('uls');
                        self.sourceSelector.unbind('.uls');
                        self.targetSelector.unbind('.uls');
                        self.activateULS(self.sourceSelector, self.onSelectSource, self.getSourceSelectorPosition, self.sourceLanguages);
                        self.activateULS(self.targetSelector, self.onSelectTarget, self.getTargetSelectorPosition, self.targetLanguages);
                    }
                }, 50);
            });

            // Use en as a fallback for i18n; populateDefaults() will load other languages if preferred
            updateLanguage('en');
            self.populateDefaults(self.sourceLanguages, self.targetLanguages);

            if (self.source && self.target) {
                self.fetchArticles();
            }

            //search feedback/suggestion
            self.suggestSearches();
        });

        self.suggestSearches = function () {
            //TODO:
            //    1. not sure why adding id attribute in the text input field breaks things
            //    2. using addEvent below. Could have used jquery.
            var callbackOnSelect = function(event, val) {
                $('input[name=seedArticle]').val(val.title);
                self.fetchArticles();
            };

            var typeAhead = new WMTypeAhead('#seed-container', 'input[name=seedArticle]', callbackOnSelect);
            addEvent($('input[name=seedArticle]')[0], 'input',  function(){
                typeAhead.query(this.value, self.source);
            });
        };

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

            if (!self.source && browserLanguages.length > 0) {
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
            if (!self.target && browserLanguages.length > 0) {
                if (browserLanguages.length) {
                    self.setTarget(browserLanguages[Math.floor(Math.random() * browserLanguages.length)]);
                    self.origin = 'browser_settings';
                }
            }

            $('input[name=seedArticle]').val(window.translationAppGlobals.seed);
        };

    </script>
</gf-input>
