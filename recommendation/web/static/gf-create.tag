<gf-create>
    <div id="createModal" class="modal fade" role="dialog" tabindex="-1">
        <div class="modal-dialog" role="document">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="gf-modal-header-container">
                        <span class="gf-modal-title">{$.i18n('create-title')}</span>
                        <span class="gf-icon gf-icon-close gf-clickable" data-dismiss="modal" title="{$.i18n('modal-close')}"></span>
                    </div>
                </div>
                <div class="modal-body">
                    <div class="form-group">
                        <input id="targetTitle" type="text" class="form-control"
                               placeholder="{$.i18n('create-title-input-placeholder')}" oninput={validateTitle}>
                    </div>
                    <div class={alert: true, invisible: errorMessage === '', alert-danger: true} role="alert">
                        <strong>{$.i18n('create-warning')}</strong> {errorMessage} <a class="alert-link" target="_blank" href={errorLink}>{errorLink}</a>
                    </div>
                </div>
                <div class="modal-footer">
                    <div class="gf-modal-footer-container">
                        <a role="button" class={btn: true, btn-primary: true, gf-flex-float-right: true, disabled: !isValid}
                           target="_blank" onclick={logCreateAction} href={isValid ? createRoot + encodeURIComponent(targetTitle) : '#'}>
                            {$.i18n('create-action')}
                        </a>
                    </div>
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
        self.createRoot = 'https://' + opts.to + '.wikipedia.org/w/index.php?action=edit&redlink=1&title=';
        self.existsLinkRoot = 'https://' + opts.to + '.wikipedia.org/wiki/';
        self.targetTitle = '';
        self.isValid = false;
        self.errorMessage = '';
        self.errorLink = '';
        self.existsQueryRoot = 'https://' + opts.to + '.wikipedia.org/w/api.php';

        self.checkTitle = function () {
            var targetTitle = $('#targetTitle')[0].value;

            if ( targetTitle === '' ) {
                self.setInvalid($.i18n('create-error-empty'), '');
                return;
            }
            if ( /\|/.test(targetTitle) ) {
                self.setInvalid($.i18n('create-error-invalid-character'), '');
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
                    self.setInvalid($.i18n('create-error-exists', '"' + title + '"'), self.existsLinkRoot + title);
                }

                if ( response.query.pages[pageid].invalid !== undefined ) {
                    self.setInvalid($.i18n('create-error-invalid', '"' + title + '"'), self.existsLinkRoot + title);
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

        self.logCreateAction = function() {
            logAction(self.title, 'create_from_scratch', self.targetTitle);
            return true;
        };

        validateTitle (e) {
            if (timeout) {
                clearTimeout(timeout);
            }
            timeout = setTimeout(self.checkTitle, inputDelayMillis);
        }

    </script>

</gf-create>
