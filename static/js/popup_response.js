const data = JSON.parse(document.getElementById('popupResponse').getAttribute('data-popup-response'));
opener.onAfterPopupClosed(window, data);