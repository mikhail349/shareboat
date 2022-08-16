$(document).ready(() => {
    console.log(window.userPk);
    const 
        getMessagesApi = `/chat/api/get_new_support_messages/${window.userPk}/`,
        sendMessageApi = `/chat/api/send_support_message/${window.userPk}/`;
    new MessageHandler(getMessagesApi, sendMessageApi);
})