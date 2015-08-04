<menu class="ui pointing menu">
    <div class="right menu">
        <div class="ui pointing personalize dropdown link item">
            Personalize <i class="dropdown icon"></i>
            <div class="menu">
              <div class="item">Login to Wikipedia</div>
              <div class="item" onclick={ enableArticle }>With an Article</div>
            </div>
        </div>

        <div if={ seedArticleVisible } class="item">
            <input placeholder=" seed article" name="seedArticle"/>
        </div>

        <a each={ opts.items }
           class={ item: true, active: parent.selected === view }
           onclick={ parent.navigate }
        >{ view }</a>
    </div>

    <script>
        this.selected = null
        this.seedArticleVisible = false

        enableArticle(e) {
            this.seedArticleVisible = true
        }

        navigate(e) {
            var url = this.seedArticle.value ?
                e.item.view + '/' + this.seedArticle.value :
                e.item.view

            riot.route(url)

            this.selected = e.item.view
        }

        this.on('mount', function (){
            $('.ui.dropdown').dropdown();
        });
    </script>
</menu>
