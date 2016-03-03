<articles>

    <div class="row text-xs-center" if={ !articles || !articles.length }>
        {articles['error']}
    </div>
    <div class="list-group row">
        <div each={articles} class="col-sm-6 m-b-1" onmouseover={hoverIn} onmouseout={hoverOut}>
            <div class="btn-group list-group-item p-a-0" style="height: 7rem;">
                <button type="button" class="btn btn-secondary p-y-0 borderless" style="width: 90%; height: 100%;" onclick={preview}
                        data-toggle="popover" data-placement="top" data-trigger="hover" data-content={title}>
                    <div class="m-r-1 pull-xs-left" style="width: 90px; height: 100%">
                        <img class="img-rounded vertical-center" src={thumbnail} if={thumbnail}/>
                    </div>
                    <h5 class="text-xs-left m-t-1 m-b-0 no-overflow"
                        style="height: 1.5rem;">
                        {title}
                    </h5>
                    <p class="text-xs-left m-t-0 m-b-0 no-overflow"
                        style="height: 1.5rem;">
                        {description}
                    </p>
                    <div class="pull-xs-left">
                        <small class="text-muted">{pageviews} recent views</small>
                    </div>
                </button>
                <button type="button" class="btn btn-secondary dropdown-toggle borderless pull-xs-right" data-toggle="dropdown"
                        style="width: 10%; height: 100%;">
                    <span hidden={!hovering}>&#x2691;</span>
                </button>
                <div class="dropdown-menu dropdown-menu-right">
                    <button type="button" class="dropdown-item" onclick={addToPersonalBlacklist}>
                        Remove, I am not interested
                    </button>
                    <button type="button" class="dropdown-item" onclick={addToGlobalBlacklist}>
                        Remove, this is not notable for {target} wikipedia
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

        var thumbQuery = 'https://{source}.wikipedia.org/w/api.php?action=query&pithumbsize=90&format=json&prop=pageimages&titles=';

        self.detail = function (article) {
            return $.ajax({
                url: thumbQuery.replace('{source}', self.source) + article.title,
                dataType: 'jsonp',
                contentType: 'application/json'
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
                if (Object.keys(descriptions).length == 0)
                    return;
                var lang = Object.keys(data.entities[id].descriptions)[0];
                var description = data.entities[id].descriptions[lang].value;
                article.description = description
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
        };

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

        hoverIn (e) {
            e.item.hovering = true;
        }

        hoverOut (e) {
            e.item.hovering = false;
        }

        // kick off the loading of the articles
        var promises = self.articles.map(self.detail).concat(self.articles.map(self.get_description));
        $.when.apply(this, promises).then(self.refresh);

        //seems broken
        self.on('update', function () {
            // add tooltips for truncated article names
            $.each($('[data-toggle="popover"]'), function (index, item) {
                var header = $(item)[0].getElementsByTagName('h6')[0];
                if ($(header.scrollWidth)[0] > $(header.offsetWidth)[0]) {
                    $(item).popover({
                        template: '<div class="popover" role="tooltip"><div class="popover-arrow"></div><div class="popover-content"></div></div>'
                    });
                } else {
                    $(item).popover('dispose');
                }
            });
        });
    </script>

</articles>
