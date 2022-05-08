$(document).ready(() => { 
    //$('#menu ul').first().html('');
    //$('a.navbar-brand').text(window.boatName);

    const 
        longPoolingApi=`/chat/api/get_new_messages_boat/${window.boatId}/`,
        sendMessageApi=`/chat/api/send_message_boat/${window.boatId}/`

    new MessageHandler(longPoolingApi, sendMessageApi);
});