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
                    class="rounded-circle"
                    alt 
                />
            `
        }
        return '<div style="width:32px; height:32px"></div>'
    }

    function formatSentAt(dt) {
        const d = dt.getDate();
        const m = dt.getMonth() + 1;
        return `${(d>9 ? '' : '0') + d}.${(m>9 ? '' : '0') + m}.${dt.getFullYear()}, ${dt.getHours()}:${dt.getMinutes()}`
    }

    function appendMessage(message) {
        const bg = message.is_out ? 'list-group-item-primary ' : 'list-group-item-secondary ';
        
        $msgContainer.append(`
            <div class="list-group-item ${bg} mb-3 rounded border pb-0" style="width: fit-content;">
                <div class="d-flex gap-3">
                    ` + getAvatar(message) + `
                    <div class="d-flex">
                        ${message.text.replaceAll('\r\n', '<br>')}
                    </div>
                </div>
                <small class="float-end">${formatSentAt(new Date(message.sent_at))}</small>
            </div>  
        `);   
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

    $btnSend.on('click', function(e) {
        sendMessage();        
    });

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
            url: `/chat/api/get_new_messages_booking/${window.bookingId}/`,
        }).done(function(data) {
            console.log(data.data);
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