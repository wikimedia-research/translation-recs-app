<gf-articles>
    <div class="gf-all-suggestions-container">
        <div each={articles} class="gf-suggestion-container">
            <div class="gf-suggestion-image"
                 onclick={preview} style="background-image: url('{thumbnail}');"></div>
            <div class="gf-suggestion-body-container" onclick={preview}>
                <div class="gf-suggestion-title-container">
                    <span class="gf-suggestion-title-popover">{title}</span>
                    <span class="gf-suggestion-title">{title}</span>
                </div>
                <span class="gf-suggestion-text">{description}</span>
            </div>
            <div class="gf-suggestion-footer-container dropup">
                <span class="gf-suggestion-views text-muted">{$.i18n('article-pageviews', pageviews)}</span>
                <span class="gf-suggestion-flag gf-icon gf-icon-flag gf-clickable dropdown-toggle" data-toggle="dropdown"
                      title={$.i18n('article-flag')}></span>
                <div class="dropdown-menu dropdown-menu-right">
                    <button type="button" class="dropdown-item" onclick={addToPersonalBlacklist}>
                        {$.i18n('article-flag-not-interesting')}
                    </button>
                    <button type="button" class="dropdown-item" onclick={addToGlobalBlacklist}>
                        {$.i18n('article-flag-not-notable', target)}
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        var self = this;

        self.articles = opts.articles || [];
        self.source = opts.source || 'no-source-language';
        self.target = opts.target || 'no-target-language';

        var thumbQuery = 'https://{source}.wikipedia.org/w/api.php?action=query&pithumbsize=512&format=json&prop=pageimages&titles=';

        self.detail = function (article) {
            return $.ajax({
                url: thumbQuery.replace('{source}', self.source) + article.title,
                dataType: 'jsonp',
                contentType: 'application/json'
            }).done(function (data) {
                var id = Object.keys(data.query.pages)[0],
                    page = data.query.pages[id];

                article.id = id;
                article.linkTitle = encodeURIComponent(article.title);
                article.title = page.title;
                article.thumbnail = page.thumbnail ? page.thumbnail.source : 'static/gapfinder/images/lines.svg';
                article.hovering = false;
                self.update();

            });
        };

        var descriptionQuery = 'https://wikidata.org/w/api.php?action=wbgetentities&format=json&props=descriptions&languages={source}&ids='
        self.get_description = function(article) {
            var url = descriptionQuery.replace('{source}', self.source) + article.wikidata_id
            return $.ajax({
                url: url,
                dataType: 'jsonp',
                contentType: 'application/json'
            }).done(function (data) {
                var id = Object.keys(data.entities)[0];
                var descriptions = data.entities[id].descriptions;
                if (Object.keys(descriptions).length == 0) {
                    return;
                }
                var lang = Object.keys(data.entities[id].descriptions)[0];
                article.description = data.entities[id].descriptions[lang].value;
                self.update();

            });
        };

        self.remove = function (article, personal) {
            var blacklistKey = personal ? translationAppGlobals.personalBlacklistKey : translationAppGlobals.globalBlacklistKey,
                blacklist = store(blacklistKey) || {},
                wikidataId = article.wikidata_id;

            if (personal) {
                // store wikidata id without associating to source or target, so
                // that this article can always be blacklisted, regardless of languages
                blacklist[wikidataId] = true;
                logAction(article.title, 'flag_not_interested');
            } else {
                // store the wikidata id relative to the target, so that this article
                // can be ignored regardless of source language
                blacklist[self.target] = blacklist[self.target] || {};
                blacklist[self.target][wikidataId] = true;
                logAction(article.title, 'flag_not_notable');
            }

            store(blacklistKey, blacklist);

            var index = self.articles.indexOf(article);
            self.articles.splice(index, 1);
            self.update();
        };

        addToPersonalBlacklist (e) {
            this.remove(e.item, true);
        }

        addToGlobalBlacklist (e) {
            this.remove(e.item, false);
        }

        preview (e) {
            riot.mount('gf-preview', {
                articles: self.articles,
                title: e.item.title,
                from: self.source,
                to: self.target,
                remove: self.remove,
            });
        }

        // kick off the loading of the articles
        var promises = self.articles.map(self.detail).concat(self.articles.map(self.get_description));
        $.when.apply(this, promises).then(self.refresh);

        self.on('update', function () {
            // set tooltip text to be smaller for truncated titles
            // otherwise, the font will remain the same size as the title
            // and not be visibly different when hovered over
            $.each($('.gf-suggestion-title'), function (index, item) {
                if ($(item.scrollWidth)[0] > $(item.offsetWidth)[0]) {
                    var popover = $(item).parent().children('.gf-suggestion-title-popover');
                    $(popover).css('font-size', '1rem');
                    $(popover).css('line-height', '1rem');
                }
            });
        });
    </script>

</gf-articles>
