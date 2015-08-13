<articles class="ui centered grid container tight cards">

    <p if={ !articles || !articles.length } class="ui warning message">
        No articles found.  Try without a seed article, or let us know if this keeps happening.
    </p>

    <div each={ articles } class="card"
        onmouseover={ hoverIn }
        onmouseout={ hoverOut }>

        <a onclick={ preview }>
            <img src={ thumbnail } class="ui left floated image" />
            <h3>{ title }</h3>
            <span class="meta">viewed { pageviews } times recently</span>
        </a>
        <span class={ hidden: !hovering }>

            <button class="ui top right corner icon button pointing personalize dropdown link">
                <i class="flag icon"></i>
                <div class="menu">
                    <div class="item" onclick={ addToPersonalBlacklist }>
                        Remove, I am not interested
                    </div>
                    <div class="item" onclick={ addToGlobalBlacklist }>
                        Remove, this is not notable for { target } wikipedia
                    </div>
                </div>
            </button>
        </span>
    </div>

    <preview></preview>


    <script>
        var self = this;

        self.articles = opts.articles || [];
        self.source = opts.source || 'no-source-language';
        self.target = opts.target || 'no-target-language';

        var thumbQuery = 'https://{source}.wikipedia.org/w/api.php?action=query&pithumbsize=50&format=json&prop=pageimages&titles=';

        self.detail = function (article) {
            return $.ajax({
                url: thumbQuery.replace('{source}', self.source) + article.title,
                dataType: 'jsonp',
                contentType: 'application/json',

            }).done(function (data) {
                var id = Object.keys(data.query.pages)[0],
                    page = data.query.pages[id];

                article.id = id;
                article.linkTitle = article.title;
                article.title = page.title;
                article.thumbnail = page.thumbnail ? page.thumbnail.source : null;
                article.hovering = false;
                self.update();

            });
        }

        self.remove = function (article, personal) {

            var blacklistKey = personal ? translationAppGlobals.personalBlacklistKey : translationAppGlobals.globalBlacklistKey,
                blacklist = store(blacklistKey) || {},
                wikidataId = article.wikidata_id;

            if (personal) {
                // store wikidata id without associating to source or target, so
                // that this article can always be blacklisted, regardless of languages
                blacklist[wikidataId] = true;

            } else {
                // store the wikidata id relative to the target, so that this article
                // can be ignored regardless of source language
                blacklist[self.target] = blacklist[self.target] || {};
                blacklist[self.target][wikidataId] = true;
            }

            store(blacklistKey, blacklist);

            var index = self.articles.indexOf(article);
            self.articles.splice(index, 1);
            self.update();
        }

        addToPersonalBlacklist (e) {
            this.remove(e.item, true);
        }

        addToGlobalBlacklist (e) {
            this.remove(e.item, false);
        }

        preview (e) {
            riot.mount('preview', {
                articles: self.articles,
                title: e.item.title,
                from: self.source,
                to: self.target,
                remove: self.remove,
            });
        }

        refresh () {
            $('.ui.dropdown', self.root).dropdown();
        }

        hoverIn (e) {
            e.item.hovering = true;
        }

        hoverOut (e) {
            e.item.hovering = false;
        }

        // kick off the loading of the articles
        var promises = self.articles.map(self.detail);
        $.when.apply(this, promises).then(self.refresh);
    </script>

</articles>
