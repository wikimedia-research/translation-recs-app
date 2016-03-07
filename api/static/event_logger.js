var logUIRequest = function (
    sourceLanguage,
    targetLanguage,
    seed,
    searchAlgorithm,
    userId,
    campaign,
    campaignCondition
) {
    var schema = 'TranslationRecommendationUIRequests';
    var revision = 15405403;
    var event = {
        'timestamp': Math.floor(new Date().getTime() / 1000),
        'userAgent': navigator.userAgent,
        'sourceLanguage': sourceLanguage,
        'targetLanguage': targetLanguage,
        'userToken': getUserToken(),
        'requestToken': getNewRequestToken()
    };
    if ( seed !== undefined ) {
        event['seed'] = seed;
    }
    if ( searchAlgorithm !== undefined ) {
        event['searchAlgorithm'] = searchAlgorithm;
    }
    if ( userId !== undefined ) {
        event['userId'] = userId;
    }
    if ( campaign !== undefined ) {
        event['campaign'] = campaign;
    }
    if ( campaignCondition !== undefined ) {
        event['campaignCondition'] = campaignCondition;
    }
    logEvent(schema, revision, event);
};

var logAction = function (
    pageTitle,
    action
) {
    var schema = 'TranslationRecommendationUserAction';
    var revision = 15419947;
    var event = {
        'requestToken': getExistingRequestToken(),
        'pageTitle': pageTitle,
        'action': action
    };
    logEvent(schema, revision, event);
};

var getUserToken = function () {
    var token = getCookie('userToken');
    if (!token) {
        token = generateToken();
        document.cookie = 'userToken=' + token;
    }
    return token;
};

var getNewRequestToken = function () {
    var token = generateToken();
    document.cookie = 'requestToken=' + token;
    return token;
};

var getExistingRequestToken = function () {
    return getCookie('requestToken');
};

var generateToken = function () {
    // http://stackoverflow.com/questions/105034/create-guid-uuid-in-javascript?lq=1
    var d = new Date().getTime();
    if (window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
};

var getCookie = function (name) {
    // adapted from
    // https://developer.mozilla.org/en-US/docs/Web/API/Document/cookie/Simple_document.cookie_framework
    return document.cookie.replace(new RegExp("(?:(?:^|.*;)\\s*" + name + "\\s*\\=\\s*([^;]*).*$)|^.*$"), "$1") || null;
};

var logEvent = function(schema, revision, event) {
    var payload = {
        schema: schema,
        revision: revision,
        wiki: 'metawiki',
        event: event
    };

    var url = window.translationAppGlobals.eventLoggerUrl + '?' + encodeURIComponent(JSON.stringify(payload));

    $.get(url);
};
