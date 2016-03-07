<Recommend>
    <div class="jumbotron jumbotron-fluid">
        <div class="container">
            <h2>Wikipedia Translation Recommendations</h2>
            <p>Select a language pair and seed article</p>
            <form class="form-inline" role="form" autocomplete="off">
                <div class="form-group">
                    <select class="c-select form-control" name="source">
                        <option>Source Language</option>
                        <option each={code in sources} value={code}>
                            {code}
                        </option>
                    </select>
                </div>
                <div class="form-group">
                    <select class="c-select form-control" name="target">
                        <option>Target Language</option>
                        <option each={code in targets} value={code}>
                            {code}
                        </option>
                    </select>
                </div>
                <div class="form-group">
                    <input type="text" class="form-control" placeholder="Seed Article (Optional)" name="seedArticle" />
                </div>
                <button type="button" class="btn btn-default" onclick={fetchArticles} >Submit</button>
            </form>
        </div>
    </div>
    <div class="container">
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
        self.defaultSource = window.translationAppGlobals.s;
        self.defaultTarget = window.translationAppGlobals.t;
        self.defaultSeed = window.translationAppGlobals.seed;
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

            var seed;
            if (this.seedArticle.value) {
                url += '&article=' + encodeURIComponent(this.seedArticle.value);
                seed = this.seedArticle.value;
            }

            logUIRequest(self.source.value, self.target.value, seed);

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
            if ($.inArray(self.defaultSource, self.languagePairs['source']) !== -1) {
                $('select[name=source]').val(self.defaultSource);
            }
            if ($.inArray(self.defaultTarget, self.languagePairs['target']) !== -1) {
                $('select[name=target]').val(self.defaultTarget);
            }
            $('input[name=seedArticle]').val(self.defaultSeed);
            //self.fetchArticles();
        });

    </script>
</Recommend>
