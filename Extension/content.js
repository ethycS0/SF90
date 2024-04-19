browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.displayWarning) {
      var warningBanner = document.createElement('div');
      warningBanner.style.background = 'red';
      warningBanner.style.color = 'white';
      warningBanner.style.padding = '10px';
      warningBanner.style.position = 'fixed';
      warningBanner.style.top = '0';
      warningBanner.style.width = '100%';
      warningBanner.textContent = 'This site may be unsafe. Proceed with caution.';
      document.body.appendChild(warningBanner);
    }
  });