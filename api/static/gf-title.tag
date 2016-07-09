<gf-title>
    <div class="container-fluid m-t-1">
        <div class="row">
            <div class="dropdown">
                <div class="col-xs-12">
                    <span class="icon icon-title icon-lightbulb"></span>
                    <span class="title-display" data-i18n="title-wikipedia">Wikipedia</span>
                    <span class="title-display-strong" data-i18n="title-gapfinder">GapFinder</span>
                    <span class="title-display-version" data-i18n="title-beta">beta</span>
                    <span class="icon icon-title icon-menu dropdown-toggle" style="cursor:pointer"
                          data-toggle="dropdown"></span>
                    <div class="dropdown-menu dropdown-menu-right m-r-1">
                        <button class="dropdown-item" type="button"
                                data-toggle="modal" data-target="#howToModal" data-i18n="menu-how-to">How to</button>
                        <button class="dropdown-item" type="button"
                                data-toggle="modal" data-target="#aboutModal" data-i18n="menu-about">About</button>
                        <a class="dropdown-item" href="https://meta.wikimedia.org/wiki/Research_talk:Increasing_article_coverage/Tool"
                           target="_blank" data-i18n="menu-feedback">Feedback</a>
                        <a class="dropdown-item" href="https://github.com/wikimedia-research/translation-recs-app"
                           target="_blank" data-i18n="menu-source-code">Source code</a>
                        <a class="dropdown-item" href="https://wikimediafoundation.org/wiki/Recommendations_Tool_Privacy_Statement"
                           target="_blank" data-i18n="menu-privacy-statement">Privacy statement</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="howToModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal">
                        <h4 class="modal-title">&#x274c;</h4>
                    </button>
                    <h4 class="modal-title" data-i18n="menu-how-to">How to</h4>
                </div>
                <div class="modal-body">
                    <p>GapFinder helps you discover articles that exist in one language but are missing in another.

                    <p>Start by selecting a source language and a target language. GapFinder will find trending articles in the source that  are missing in the target.

                    <p>If you are interested in a particular topic area, provide a seed article in the source language, and GapFinder will find related articles missing in the target.

                    <p>Click on a card to take a closer look at a missing article to see if you would like to create it from scratch or translate it.
                </div>
            </div>
        </div>
    </div>

    <div id="aboutModal" class="modal fade" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <button type="button" class="close" data-dismiss="modal">
                        <h4 class="modal-title">&#x274c;</h4>
                    </button>
                    <h4 class="modal-title" data-i18n="menu-about">About</h4>
                </div>
                <div class="modal-body">
                    <p>We are a team of researchers, developers, and designers in the Wikimedia Foundation and Stanford University interested in identifying gaps of knowledge across the more than 160 active language editions of Wikipedia.

                    <p>Back in 2015, we started a project to identify missing content in Wikipedia, rank it by its importance, and recommend the ranked missing content to Wikipedia’s volunteer editors based on their interests as captured by their editor history. We ran an experiment in June 2015 in French Wikipedia where we showed that by emailing recommendations to volunteer editors we can triple the article creation rate in Wikipedia while maintaining the current level of quality in Wikipedia articles. If you are interested to learn more about that research, you can read more about it <a href = "http://arxiv.org/abs/1604.03235"> here</a>.

                    <p>Encouraged by the result of the experiment, we have developed Wikipedia GapFinder, an app that helps you find missing content in any language for which there is a Wikipedia edition. GapFinder can help you to easily find articles to create in the language of your choice. It also lets you personalize the recommendations by providing a seed article, an article that you would like to receive similar missing article recommendations.

                    <p>GapFinder is a research app at the moment. By using it, you will make more content available in your local language, and help us understand how we can improve the app. Please share your feedback on <a href="https://meta.wikimedia.org/wiki/Research_talk:Increasing_article_coverage/Tool" target="_blank">the tool's talk page</a>.

                    <h6>In the media:</h6>
                        <ul>
                            <li>
                                <a href="http://www.lemonde.fr/sciences/article/2016/01/11/wikipedia-la-connaissance-en-mutation_4845347_1650684.html" target="_blank"> Le Monde: Wikipédia, quinze ans de recherches</a>
                            </li>
                            <li>
                                <a href="https://news.stanford.edu/2016/04/14/stanford-wikimedia-researchers-create-tool-boost-article-creation-local-language-wikipedias/" target="_blank">Stanford and Wikimedia researchers create a tool to boost article creation in local language Wikipedias</a>
                            </li>
                        </ul>
                </div>
            </div>
        </div>
    </div>
</gf-title>
