<create_article>
    <div id="createModal" class="modal fade" role="dialog" tabindex="-1">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="container-fluid">
                        <div class="row">
                            <h4 class="modal-title col-xs-8">New Article</h4>
                            <button type="button" class="btn btn-secondary borderless pull-xs-right col-xs-1" data-dismiss="modal">
                                <h4 class="m-y-0">&#x274c;</h4>
                            </button>
                        </div>
                    </div>

                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <input id="targetTitle" type="text" class="form-control" placeholder="Translation title" oninput={validateTitle}>
                    </div>
                    <div class={alert: true, invisible: errorMessage === '', alert-danger: true} role="alert">
                        <strong>Warning!</strong> {errorMessage}<a class="alert-link" target="_blank" href={errorLink}>{errorLink}</a>.
                    </div>
                </div>
                <div class="modal-footer">
                    <a role="button" class={btn: true, btn-primary: true, disabled: !isValid} target="_blank" href={isValid ? createRoot + targetTitle : '#'}>Create</a>
                </div>
            </div>
        </div>
    </div>

    <script>
        var self = this;
        var timeout;
        var inputDelayMillis = 200;

        self.title = opts.title || '';
        self.to = opts.to || '';
        self.from = opts.from || '';
        self.createRoot = 'https://' + opts.to + '.wikipedia.org/w/index.php?action=edit&title=';
        self.existsLinkRoot = 'https://' + opts.to + '.wikipedia.org/wiki/';
        self.targetTitle = '';
        self.isValid = false;
        self.errorMessage = '';
        self.errorLink = '';
        self.existsQueryRoot = 'https://' + opts.to + '.wikipedia.org/w/api.php';

        self.checkTitle = function () {
            var targetTitle = $('#targetTitle')[0].value;

            if ( targetTitle === '' ) {
                self.setInvalid('Title must not be empty', '');
                return;
            }
            if ( /\|/.test(targetTitle) ) {
                self.setInvalid('Invalid character in title ( "|" )', '');
                return;
            }

            $.ajax({
                url: self.existsQueryRoot,
                data: {
                    action: 'query',
                    redirects: true,
                    indexpageids: true,
                    format: 'json',
                    titles: targetTitle
                },
                dataType: 'jsonp'
            }).done(function (response) {
                var pageid = response.query.pageids[0];
                var title = response.query.pages[pageid].title;

                if ( response.query.pages[pageid].missing !== undefined ) {
                    self.targetTitle = title;
                    self.setValid();
                } else {
                    self.setInvalid('Page already exists at ', self.existsLinkRoot + title);
                }

                if ( response.query.pages[pageid].invalid !== undefined ) {
                    self.setInvalid('Page is invalid at ', self.existsLinkRoot + title);
                }
            });
        };

        self.setInvalid = function (message, link) {
            self.isValid = false;
            self.errorMessage = message;
            self.errorLink = link;
            var input = $('#targetTitle')[0];
            input.classList.remove('form-control-success');
            input.parentElement.classList.remove('has-success');
            input.classList.add('form-control-danger');
            input.parentElement.classList.add('has-danger');
            self.update();
        };

        self.setValid = function () {
            self.isValid = true;
            self.errorMessage = '';
            var input = $('#targetTitle')[0];
            input.classList.remove('form-control-danger');
            input.parentElement.classList.remove('has-danger');
            input.classList.add('form-control-success');
            input.parentElement.classList.add('has-success');
            self.update();
        };

        validateTitle (e) {
            if (timeout) {
                clearTimeout(timeout);
            }
            timeout = setTimeout(self.checkTitle, inputDelayMillis);
        }

    </script>

</create_article>
