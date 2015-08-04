<Recommend class="ui">

    <div class="ui nine column centered grid">
        <div class="row">
            <h2 class="header">Articles Recommended for Translation</h2>
        </div>

        <div class="stackable row">
            <div class="three wide aligned column">
                <h3>From</h3>
                <select class="ui personalize dropdown" name="source">
                    <option value="test_source">English</option>
                    <option disabled>(more coming soon)</option>
                </select>
            </div>
            <div class="tablet computer only three wide bottom aligned column">
                <i class="ui big right arrow icon"></i>
            </div>
            <div class="three wide aligned column">
                <h3>To</h3>
                <select class="ui personalize dropdown" name="target">
                    <option value="test_target">español</option>
                    <option disabled>(more coming soon)</option>
                </select>
            </div>
        </div>

        <div class="row"></div>

        <div class="ui centered grid container tight cards">

            <p if={ !articles } class="ui warning message">
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
                    <button class="ui top right corner icon button" onclick={ remove }>
                        <i class="remove icon"></i>
                    </button>
                </span>
            </div>
        </div>
    </div>

    <preview></preview>

    <script>
        var self = this;

        var url = '/api?s=' + self.source.value + '&t=' + self.target.value;

        if (opts.seedArticle) {
            url += '&article=' + opts.seedArticle;
        }

        $.ajax({
            url: url,
        }).done(function (data) {
            self.articles = data.articles;
            self.articles.forEach(self.detail);
            self.refresh();
        });

        var thumbQuery = 'https://en.wikipedia.org/w/api.php?action=query&pithumbsize=50&format=json&prop=pageimages&titles=';

        var self = this;
        self.detail = function (article) {
            $.ajax({
                url: thumbQuery + article.title,
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

        remove (e) {
            var index = this.articles.indexOf(e.item);
            this.articles.splice(index, 1);
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
            $('.ui.extra .button').popup();
        }

        this.on('mount', function (){
            this.refresh();
        });

        hoverIn (e) {
            e.item.hovering = true;
        }

        hoverOut (e) {
            e.item.hovering = false;
        }

    </script>
</Recommend>
