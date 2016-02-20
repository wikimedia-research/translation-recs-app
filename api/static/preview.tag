<preview>
    <div id="previewModal" class="modal fade" role="dialog" tabindex="-1">
        <div class="modal-dialog modal-lg" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="container-fluid">
                        <div class="row">
                            <h4 class="modal-title col-xs-8">{title}</h4>
                            <button type="button" class="btn btn-secondary borderless pull-xs-right col-xs-1" data-dismiss="modal">
                                <h4 class="m-y-0">&#x274c;</h4>
                            </button>
                            <a role="button" class="btn btn-secondary borderless pull-xs-right col-xs-1" target="_blank" href={articleLink}>
                                <h4 class="m-y-0">&#x2197;</h4>
                            </a>
                        </div>
                    </div>

                </div>
                <div class="modal-body">
                    <div class="embed-responsive embed-responsive-4by3">
                        <iframe id="previewDiv"></iframe>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" onclick={left}
                            class={btn: true, btn-secondary: true, borderless: true, pull-xs-left: true,
                            disabled: showIndex === 0}>
                        <h4 class="m-y-0"><</h4>
                    </button>
                    <button type="button" class="btn btn-secondary dropdown-toggle borderless pull-xs-left" data-toggle="dropdown">
                        <h4 class="m-y-0">&#x2691;</h4>
                    </button>
                    <div class="dropdown-menu dropdown-menu-left">
                        <button type="button" class="dropdown-item" onclick={addToPersonalBlacklist}>
                            Remove, I am not interested
                        </button>
                        <button type="button" class="dropdown-item" onclick={addToGlobalBlacklist}>
                            Remove, this is not notable for {opts.to} wikipedia
                        </button>
                    </div>
                    <button type="button" onclick={right}
                            class={btn: true, btn-secondary: true, borderless: true, pull-xs-left: true,
                            disabled: showIndex > (articles.length - 2)}>
                        <h4 class="m-y-0">></h4>
                    </button>
                    <div class="btn-group">
                        <a role="button" class="btn btn-primary" target="_blank" href={translateLink}>Translate</a>
                        <button type="button" class="btn btn-primary dropdown-toggle" data-toggle="dropdown">
                            <span class="sr-only">Toggle Dropdown</span>
                        </button>
                        <div class="dropdown-menu dropdown-menu-right">
                            <button class="btn dropdown-item" data-dismiss="modal" onclick={showCreate}>Create from scratch</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <create_article></create_article>

    <script>
        var self = this;

        self.articles = opts.articles || [];
        self.title = opts.title || '';
        self.to = opts.to;
        self.from = opts.from;
        self.translateRoot = '//' + opts.from + '.wikipedia.org/wiki/Special:ContentTranslation?' +
            'from=' + opts.from +
            '&to=' + opts.to +
            '&campaign=' + translationAppGlobals.campaign;

        self.articleRoot = '//' + opts.from + '.wikipedia.org/wiki/';

        self.index = -1;
        for (var i=0; i<self.articles.length; i++) {
            if (self.articles[i].title === self.title) {
                self.showIndex = i;
                break;
            }
        }

        var previewRoot = 'https://rest.wikimedia.org/' + opts.from + '.wikipedia.org/v1/page/html/';

        self.show = function () {
            var showing = self.articles[self.showIndex];
            self.title = showing.title;
            self.translateLink = self.translateRoot + '&page=' + showing.linkTitle;
            self.articleLink = self.articleRoot + showing.linkTitle;
            self.previewUrl = previewRoot + showing.linkTitle;

            $('#previewDiv').attr("srcdoc", "Loading...");

            $.get(self.previewUrl).done(function (data) {
                data = data.replace('</head>', '<style type="text/css">.mw-body {margin: 0; border: none; padding: 0;}</style></head>');
                self.showPreview(data);
            }).fail(function (data) {
                self.showPreview('No Internet');
            });
        };

        self.showPreview = function (data) {
            $('#previewModal').on('shown.bs.modal', function (e) {
                // Necessary for Firefox, which has problems reloading the iframe
                $('#previewDiv').attr("srcdoc", data);
            });
            $('#previewDiv').attr("srcdoc", data);
            $('#previewModal').modal('show');

            self.update();
        };

        addToPersonalBlacklist () {
            opts.remove(self.articles[self.showIndex], true);
            $('#previewModal').modal('hide');
        }

        addToGlobalBlacklist () {
            opts.remove(self.articles[self.showIndex], false);
            $('#previewModal').modal('hide');
        }

        left () {
            if (self.showIndex > 0) {
                self.showIndex --;
                self.show();
            }
        }

        right () {
            if (self.showIndex < self.articles.length - 1) {
                self.showIndex ++;
                self.show();
            }
        }

        showCreate (e) {
            riot.mount('create_article', {
                title: self.title,
                to: self.to,
                from: self.from,
                remove: self.remove
            });

            $('#createModal').modal('show');
        }

        if (isFinite(self.showIndex)) {
            self.show();
        }

        $('#previewModal').on('hide.bs.modal', function (e) {
            $('#previewDiv').attr("srcdoc", "");
        });
    </script>

</preview>
