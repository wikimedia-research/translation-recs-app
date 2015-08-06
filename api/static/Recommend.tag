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
                <select class="ui personalize dropdown" name="target">
                    <option each={ code in targets } value={ code }>
                        { parent.languageCodes[code] }
                    </option>
                </select>
            </div>
        </div>

        <div class="ui middle aligned row">

            <label>
                Articles Similar To
                <input placeholder=" seed article" name="seedArticle"/>
                (optional)
            </label>

        </div>
        <div class="row">
            <button class="ui button">
                Recommend
            </button>

        </div>
        <div class="row"></div>

        <ArticleList></ArticleList>
    </div>

    <preview></preview>

    <script>
        var self = this;

        self.languagePairs = window.translationAppGlobals.languagePairs;
        self.languageCodes = window.translationAppGlobals.languageCodes;
        self.sources = Object.keys(self.languagePairs).sort();
        self.targets = [];

        var url = '/api?s=' + self.source.value + '&t=' + self.target.value;

        if (this.seedArticle.value) {
            url += '&article=' + this.seedArticle.value;
        }

        $.ajax({
            url: url,
        }).done(function (data) {
            console.log(data.articles);
            riot.mount('ArticleList', {articles: data.articles});
        });

        refreshUI () {
            $('.ui.dropdown').dropdown();
        }

        refreshTargets () {
            self.targets = self.languagePairs[self.source.value].sort();
            self.update();
            // have to give a kick to the semantic ui dropdown
            $('.ui.dropdown[name=target]').dropdown();
        }

        this.on('mount', function (){
            this.refreshUI();
        });

    </script>
</Recommend>
