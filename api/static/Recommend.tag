<Recommend class="ui">

    <!--
        two buttons for remove
            filter client side

        add a list of language mappings and make the dropdowns cascade
    -->


    <div class="ui nine column centered grid">
        <div class="row">
            <h2 class="header">Articles Recommended for Translation</h2>
        </div>

        <div class="stackable row">
            <div class="three wide aligned column">
                <h3>From</h3>
                <select class="ui personalize dropdown" name="source" onchange={ refreshTargets }>
                    <option each={ code in sources } value={ code }>
                        { parent.languageCodes[code] }
                    </option>
                </select>
            </div>
            <div class="tablet computer only three wide bottom aligned column">
                <i class="ui big right arrow icon"></i>
            </div>
            <div class="three wide aligned column">
                <h3>To</h3>
                <select class="ui personalize dropdown" name="target" onchange={ fetchArticles }>
                    <option each={ code in targets } value={ code }>
                        { parent.languageCodes[code] }
                    </option>
                </select>
            </div>
        </div>

        <div class="ui middle aligned row form">

            <div class="field">
                <label>Articles Similar To (optional)</label>
                <div class="fields">
                    <div class="field">
                        <input placeholder=" seed article" name="seedArticle"/>
                    </div>
                    <div class="field">
                        <button class="ui button" onclick={ fetchArticles }>
                            Recommend
                        </button>
                    </div>
                </div>
            </div>

        </div>
        <div class="row"></div>

        <div class="ui basic segment">
            <div class={
                    ui: true, active: fetching, dimmer: true
                }>
                <div class="ui text loader">Preparing Article Recommendations</div>
            </div>
            <articles></articles>
            <div class="ui basic segment" if={ fetching }></div>
        </div>
    </div>

    <script>
        var self = this;

        self.languagePairs = window.translationAppGlobals.languagePairs;
        self.languageCodes = window.translationAppGlobals.languageCodes;
        self.sources = Object.keys(self.languagePairs).sort();
        self.targets = [];
        self.fetching = false;

        self.fetchArticles = function () {

            self.fetching = true;

            var url = '/api?s=' + self.source.value + '&t=' + self.target.value;

            if (this.seedArticle.value) {
                url += '&article=' + this.seedArticle.value;
            }

            $.ajax({
                url: url,
            }).complete(function () {
                self.fetching = false;
                self.update();
            }).done(function (data) {
                var articles = self.filter(data.articles);

                riot.mount('articles', {
                    articles: articles,
                    source: self.source.value,
                    target: self.target.value,
                });
            });
        }

        self.filter = function (articles) {
            var personalBlacklist = store(translationAppGlobals.personalBlacklistKey) || {},
                targetWikiBlacklist = (store(translationAppGlobals.globalBlacklistKey) || {})[self.target.value] || {};

            return articles.filter(function (a) {
                return !personalBlacklist.hasOwnProperty(a.wikidata_id)
                    && !targetWikiBlacklist.hasOwnProperty(a.wikidata_id);
            });
        }

        self.refreshUI = function () {
            $('.ui.dropdown', self.root).dropdown();
        }

        self.refreshTargets = function () {
            self.targets = self.languagePairs[self.source.value].sort();
            // TODO: have to give a kick to the target semantic ui dropdown
        }

        this.on('mount', function (){
            this.refreshUI();
        });

    </script>
</Recommend>
