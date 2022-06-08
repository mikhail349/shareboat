$(document).ready(() => {
    const 
        getMessagesApi = `/chat/api/get_new_messages/`,
        sendMessageApi = `/chat/api/send_message/`;
    new MessageHandler(getMessagesApi, sendMessageApi);
})