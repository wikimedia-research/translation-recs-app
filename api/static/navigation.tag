<navigation>
    <nav class="navbar navbar-full navbar-dark bg-inverse">
        <div class="nav navbar-nav">
            <a each={ opts.items }
               class={ nav-item: true, nav-link: true, active: parent.selected === view }
               onclick={ parent.navigate }>{ view }</a>
        </div>
    </nav>

    <script>
        var self = this;
        this.selected = null;

        navigate(e) {
            this.select(e.item.view)
        }

        select(view) {
            riot.route(view);
            self.selected = view;
        }

        self.select('Recommend')
    </script>
</navigation>
