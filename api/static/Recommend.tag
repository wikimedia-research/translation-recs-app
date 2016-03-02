<Recommend>
    <div class="container">
        <div class="row m-b-1 text-xs-center">
            <h3>Articles Recommended for Translation</h3>
        </div>
        <div class="row m-b-1 text-xs-center">
            <div class="col-sm-4 col-sm-offset-1 col-xs-6">
                <h5>From</h5>
                <select class="c-select form-control form-control-lg" name="source">
                    <option each={code in sources} value={code}>
                        {code}
                    </option>
                </select>
            </div>
            <div class="col-sm-2 hidden-xs-down">
                <h1 class="display-3">&rightarrow;</h1>
            </div>
            <div class="col-sm-4 col-xs-6">
                <h5>To</h5>
                <select class="c-select form-control form-control-lg" name="target">
                    <option each={code in targets} value={code}>
                        {code}
                    </option>
                </select>
            </div>
        </div>
        <div class="row text-xs-center">
            Articles Similar To (optional)
        </div>
        <div class="row m-b-3">
            <div class="col-sm-8 col-sm-offset-2 input-group">
                <input type="text" class="form-control" placeholder="seed article" name="seedArticle" />
                <span class="input-group-btn">
                    <button type="button" class="btn btn-secondary" onclick={fetchArticles}>
                        Recommend
                    </button>
                </span>
            </div>
        </div>
        <div class="text-xs-center" if={fetching}>
            Preparing article recommendations...
        </div>
        <div class="text-xs-center alert alert-danger" role="alert" if={error}>
            <span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true"></span>
            <span class="sr-only">Error:</span>
            {error_msg} 
        </div>
        <div class={invisible: fetching || starting}>
            <articles></articles>
        </div>
    </div>

    <preview></preview>

    <script>
        var self = this;

        self.languagePairs = window.translationAppGlobals.languagePairs;
        self.sources = self.languagePairs['source'].sort();
        self.targets = self.languagePairs['target'].sort();
        self.fetching = false;
        self.starting = true;
        self.st_error = false;

        
        self.fetchArticles = function () {
            
            if (self.source.value == self.target.value) {
                self.error_msg = "From and To languages must be different"
                self.error = true;
                return
            }
            self.error = false;
            self.starting = false;
            self.fetching = true;
            self.update();

            var url = '/api?s=' + self.source.value + '&t=' + self.target.value;

            if (this.seedArticle.value) {
                url += '&article=' + this.seedArticle.value;
            }

            $.ajax({
                url: url
            }).complete(function () {
                self.fetching = false;
                self.update();
            }).done(function (data) {
                if (data.error) {
                    self.error = true;
                    self.error_msg = data.error;
                    return
                }

                var articles = self.filter(data.articles);


                riot.mount('articles', {
                    articles: articles,
                    source: self.source.value,
                    target: self.target.value
                });
            });
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
            //self.fetchArticles();
        });

    </script>
</Recommend>
