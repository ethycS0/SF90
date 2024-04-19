document.getElementById("scanButton").addEventListener("click", function() {
    // Send a message to the content script to trigger the link grabbing
    browser.tabs.query({ active: true, currentWindow: true }, function(tabs) {
      browser.tabs.sendMessage(tabs[0].id, { action: "getLinks" }, function(response) {
        console.log("Links on the webpage:", response.links);
      });
    });
  });
  