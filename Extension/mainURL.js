const lastOpenedTabDomains = new Array(5);

function logNewTabUrl(tabId, changeInfo, tab) {
    if (changeInfo.status === 'complete') {
        const tabUrl = tab.url;
        console.log("Newly loaded tab URL:", tabUrl);

        if (isInternetLink(tabUrl)) {
            if (!isSameDomainAsLastTabs(tabUrl)) {
                sendGetRequest('http://localhost:8000', { url: tabUrl })
                    .then(response => response.json())
                    .then(data => {
                        console.log('Server Response:', data);

                        try {
                            if (data.safety === "-1") {
                                browser.tabs.sendMessage(tabId, { displayWarning: true });
                            }
                        } catch (error) {
                            console.error('Error parsing JSON response:', error);
                        }
                    })
                    .catch(error => {
                        console.error('Error in sendGetRequest:', error);
                    });
            } else {
                console.log('Same domain as the last 5 tabs:', tabUrl);
            }
        } else {
            console.log('Not an internet link:', tabUrl);
        }

        updateLastOpenedTabs(tabUrl);
    }
}

function updateLastOpenedTabs(tabUrl) {
    lastOpenedTabDomains.shift();
    lastOpenedTabDomains[4] = extractDomain(tabUrl);
}

function isSameDomainAsLastTabs(tabUrl) {
    const currentDomain = extractDomain(tabUrl);
    return lastOpenedTabDomains.includes(currentDomain);
}

function extractDomain(url) {
    const match = url.match(/^https?\:\/\/([^\/?#]+)(?:[\/?#]|$)/i);
    return match && match[1];
}



browser.tabs.onUpdated.addListener(logNewTabUrl);


function sendGetRequest(url, params) {
    const queryString = Object.keys(params).map(key => key + '=' + encodeURIComponent(params[key])).join('&');
    const fullUrl = url + '?' + queryString;

    return fetch(fullUrl, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    });
}

function isInternetLink(tabUrl) {
    return tabUrl.startsWith('http://') || tabUrl.startsWith('https://');
}

browser.tabs.onUpdated.addListener(logNewTabUrl);




  