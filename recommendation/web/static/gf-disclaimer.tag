<gf-disclaimer>
    <div class="container-fluid" if={!hasDismissedDisclaimer()}>
        <div class="row">
            <div class="alert alert-info alert-dismissible fade in m-b-0" role="alert">
                <button type="button" class="close" data-dismiss="alert" title="Dismiss" onclick={setDismissedDisclaimer}>
                    <span>&times;</span>
                </button>
                This experimental tool is hosted on
                <a href="https://wikitech.wikimedia.org/wiki/Help:FAQ" class="alert-link" target="_blank">
                    Wikimedia Labs</a>.
                <a href="https://phabricator.wikimedia.org/T124503" class="alert-link" target="_blank">
                    Information collected</a>
                when you visit this site, and through your use of the
                tool, is governed by
                <a href="https://wikimediafoundation.org/wiki/Recommendations_Tool_Privacy_Statement" class="alert-link" target="_blank">
                    this privacy statement</a>
                (<strong>not</strong> the
                <a href="https://wikimediafoundation.org/wiki/Privacy_policy" class="alert-link" target="_blank">
                    main Wikimedia Privacy Policy</a>).
            </div>
        </div>
    </div>

    <script>
        var self = this;

        self.hasDismissedDisclaimer = function () {
            return getCookie('dismissedDisclaimer') == '1';
        };

        self.setDismissedDisclaimer = function () {
            document.cookie = 'dismissedDisclaimer=1';
        };
    </script>
</gf-disclaimer>