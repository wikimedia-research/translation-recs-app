<ArticleList class="ui centered grid container tight cards">

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
                <i class="dropdown icon"></i>
                <div class="menu">
                    <div class="item" onclick={ addToPersonalBlacklist }>
                        Remove, I am not interested
                    </div>
                    <div class="item" onclick={ addToGlobalBlacklist }>
                        Remove, this is not notable for { target.value } wikipedia
                    </div>
                </div>
            </button>
        </span>
    </div>


    <script>
        var self = this;

        self.articles = opts.articles;
        console.log('promising')
        var promises = self.articles.map(self.detail);
        $.when.apply(this, promises).then(self.refresh);
        console.log('waiting for promises')

        var thumbQuery = 'https://{source}.wikipedia.org/w/api.php?action=query&pithumbsize=50&format=json&prop=pageimages&titles=';

        self.detail = function (article) {
            return $.ajax({
                url: thumbQuery.replace('{source}', self.source.value) + article.title,
                dataType: 'jsonp',
                contentType: 'application/json',

            }).done(function (data) {
                var id = Object.keys(data.query.pages)[0],
                    page = data.query.pages[id];

                console.log('done ')
                article.id = id;
                article.linkTitle = article.title;
                article.title = page.title;
                article.thumbnail = page.thumbnail ? page.thumbnail.source : null;
                article.hovering = false;
                self.update();

            });
        }

        self.personalBlacklistKey = 'personal.blacklist';
        self.globalBlacklistKey = 'not.notable.blacklist';;

        self.remove = function (e, personal) {

            var blacklistKey = personal ? self.personalBlacklistKey : self.globalBlacklistKey,
                blacklist = store(blacklistKey) || {},
                wikidataId = e.item.wikidata_id;

            if (personal) {
                // store wikidata id without associating to source or target, so
                // that this article can always be blacklisted, regardless of languages
                blacklist[wikidataId] = true;

            } else {
                // store the wikidata id relative to the target, so that this article
                // can be ignored regardless of source language
                blacklist[this.target.value] = blacklist[this.target.value] || {};
                blacklist[this.target.value][wikidataId] = true;
            }

            store(blacklistKey, blacklist);

            var index = this.articles.indexOf(e.item);
            this.articles.splice(index, 1);
        }

        addToPersonalBlacklist (e) {
            this.remove(e, true);
        }

        addToGlobalBlacklist (e) {
            this.remove(e, false);
        }

        preview (e) {
            riot.mount('preview', {
                articles: self.articles,
                title: e.item.title,
                from: self.source.value,
                to: self.target.value,
            });
        }

        refresh () {
            $('.ui.dropdown').dropdown();
        }

        hoverIn (e) {
            e.item.hovering = true;
        }

        hoverOut (e) {
            e.item.hovering = false;
        }
    </script>

</ArticleList>
