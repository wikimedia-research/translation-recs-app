<menu class="ui pointing menu">
    <div class="right menu">
        <a each={ opts.items }
           class={ item: true, active: parent.selected === view }
           onclick={ parent.navigate }
        >{ view }</a>
    </div>

    <script>
        var self = this
        this.selected = null

        navigate(e) {
            this.select(e.item.view)
        }

        select(view) {
            riot.route(view)
            self.selected = view
        }

        this.on('mount', function (){
            $('.ui.dropdown').dropdown()
        });

        self.select('Recommend')
    </script>
</menu>
