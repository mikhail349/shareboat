var isOnBottom = false;

$(document).ready(() => {

    let lastScrollTop = 0,
        currentBookingDataTop = 62;

    const $bookingData = $("#bookingData");
    const bookingDataHeight = $bookingData.outerHeight();

    window.addEventListener("scroll", function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const diffScrollTop = scrollTop - lastScrollTop;
        currentBookingDataTop += -diffScrollTop;
        currentBookingDataTop = currentBookingDataTop < -bookingDataHeight ? -bookingDataHeight : currentBookingDataTop > 62 ? 62 : currentBookingDataTop;

        $bookingData.attr("style", `top: ${currentBookingDataTop}px !important;`);

        lastScrollTop = scrollTop;
    }, false);
    
    var $btnSend = $('#btnSendMessage');
    var $textArea = $('#textArea');
    var $msgContainer = $('#msgContainer');

    function getAvatar(message) {
        if (message?.sender?.avatar) {
            return `
                <img
                    height="32"
                    width="32"
                    src="${message.sender.avatar}" 
                    class="rounded-circle chat-avatar"
                    alt 
                />
            `
        }
        return '<div style="width:32px; height:32px; min-width: 32px !important; min-height: 32px;"></div>'
    }

    function formatSentAt(dt) {
        return `${('0' + dt.getDate()).slice(-2)}.${('0' + (dt.getMonth() + 1)).slice(-2)}.${dt.getFullYear()}, ${('0' + dt.getHours()).slice(-2)}:${('0'+dt.getMinutes()).slice(-2)}`;
    }

    function getMessageHtml(message) {
        const bg = message.is_out ? 'bg-primary ' : 'bg-secondary ';
        return `
            <div id="msg${message.id}" class="list-group-item border-0" style="width: fit-content;">
                <div class="d-flex gap-3">
                    ` + getAvatar(message) + `
                    <div class="d-flex ${bg} text-white rounded p-1 px-2" style="font-size: 18px; height: fit-content">${message.text.replaceAll('\r\n', '<br>')}</div>
                    <small class="float-end pe-1 align-self-end" style="font-size: 12px;">${formatSentAt(new Date(message.sent_at))}</small>
                </div>
            </div>  
        `;
    }

    function appendMessage(message) {      
        window.lastMessageId = message.id;
        $msgContainer.append(getMessageHtml(message));
    }

    function prependMessage(message) {
        $msgContainer.prepend(getMessageHtml(message));
    }
    
    if (window.messages.length > 0) {
        for (var message of window.messages) {
            appendMessage(message);
        }
        $("html, body").scrollTop($(document).height());
    }

    function getValue() {
        return $textArea.val();
    }

    $textArea.on('input', function(e) {
        const text = getValue();
        $btnSend.attr('disabled', !text);
    });

    $textArea.on('keydown', function(e) {
        if (e.keyCode === 13) {
            e.preventDefault();
        }
    })

    $textArea.on('keyup', function(e) {
        if (e.keyCode === 13) {
            e.preventDefault();
            sendMessage();
        }
    })

    $btnSend.on('click', function(e) {
        sendMessage();        
    });

    $("#btnLoadPreviousPage").on('click', function(e) {
        
        const pageNum = window.messagesPage - 1;

        if (pageNum == 1) {
            $(this).remove();
        }
        
        $.ajax({
            type: 'GET',
            url: `/chat/api/get_messages_booking/${window.bookingId}?page_num=${pageNum}`,
        }).done(function(data) {
            if (data?.data?.length > 0) {
                const messages = data.data.reverse();
                for (let message of messages) {
                    prependMessage(message);
                }
                $("html, body").scrollTop($(`#msg${messages[0].id}`).offset().top - 10);
            }      
            window.messagesPage = pageNum;
        });       
    })

    function sendMessage() {
        const text = getValue();
        if (!text) {
            return;
        }

        const formData = new FormData();
        formData.append('text', text);
        formData.append('booking_id', window.bookingId);

        $.ajax({ 
            type: "POST",
            url: `/chat/api/send_message_booking/`,
            data: formData,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 

        function onSuccess(data) {
            $textArea.val(null);
            appendMessage(data.data);
            $("html, body").animate({ scrollTop: $(document).height() });
        }

        function onError(error) {
            console.log('onError', error);
            showErrorToast(error.responseJSON.message);
        }
    }

    // Long polling
    function getNewMessages() {
        $.ajax({
            type: 'GET',
            url: `/chat/api/get_new_messages_booking/${window.bookingId}?last_message_id=${window.lastMessageId}`,
        }).done(function(data) {
            if (data?.data?.length > 0) {
                for (let message of data.data) {
                    appendMessage(message);
                }
                if (isOnBottom) {
                    $("html, body").animate({ scrollTop: $(document).height() });
                }
            }
            getNewMessages();
        }).fail(function(error) {
            if (error.status == 0) {
                getNewMessages();
            }
        })
    }

    getNewMessages();

    $(window).scroll(function() {
        isOnBottom =  ($(window).scrollTop() + $(window).height() == $(document).height());
    });
})