$(document).ready(() => {
    const 
        longPoolingApi = `/chat/api/get_new_messages_booking/${window.bookingId}/`,
        sendMessageApi = `/chat/api/send_message_booking/${window.bookingId}/`;
    new MessageHandler(longPoolingApi, sendMessageApi);
})