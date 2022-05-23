class MessageHandler {

    constructor(getMessagesApi, sendMessageApi) {
        this.GET_NEW_MESSAGES_TIMER = 2

        this.msgContainer = $('#msgContainer');
        this.btnSend = $('#btnSendMessage');
        this.textArea = $('#textArea');
        this.btnGoToBottom = $('.btn-go-to-bottom');

        this.isOnBottom = false;
        this.getMessagesApi = getMessagesApi;
        this.sendMessageApi = sendMessageApi;

        this.lastAppendedSenderId = undefined;

        var self = this;
        self.isOnBottom = false;
        self.handleBottom = self.handleBottom.bind(self);
        $(window).scroll(self.handleBottom);
        $(window).on('resize', self.handleBottom);

        this.btnGoToBottom.on('click', function() {
            $("html, body").animate({ scrollTop: $(document).height() });
        })

        this.textArea.on('input', function(e) {
            const text = self.getValue();
            self.btnSend.attr('disabled', !text);
        });
    
        this.textArea.on('keydown', function(e) {
            if (e.keyCode === 13) {
                e.preventDefault();
            }
        })
    
        this.textArea.on('keyup', function(e) {
            if (e.keyCode === 13) {
                e.preventDefault();
                self.sendMessage();
            }
        })
    
        this.btnSend.on('click', function(e) {
            self.sendMessage();        
        });

        this.appendExistingMessages();
        this.getNewMessages = this.getNewMessages.bind(this);
        this.msgTimerId = setInterval(self.getNewMessages, this.GET_NEW_MESSAGES_TIMER * 1000);
    };
    
    handleBottom() {
        const self = this;
        const scrollY = Math.ceil(window.scrollY) - 70;
        self.isOnBottom = ((window.innerHeight + scrollY) >= document.body.offsetHeight);

        if (self.isOnBottom) {
            self.btnGoToBottom.removeClass('show');
            self.btnGoToBottom.addClass('hide');
            $('#hasNewMessages').hide();
        } else {
            self.btnGoToBottom.removeClass('hide');
            self.btnGoToBottom.addClass('show');
        }
    }

    getValue() {
        return this.textArea.val();
    }

    getAvatar(message) {
        const emptyAvatar = '<div style="width:32px; height:32px; min-width: 32px !important; min-height: 32px;"></div>';

        if (this.lastAppendedSenderId == message?.sender?.id) {
            return emptyAvatar;
        }


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
        return emptyAvatar;
    }
    
    formatSentAt(dt) {
        return `${('0' + dt.getDate()).slice(-2)}.${('0' + (dt.getMonth() + 1)).slice(-2)}.${dt.getFullYear()}, ${('0' + dt.getHours()).slice(-2)}:${('0'+dt.getMinutes()).slice(-2)}`;
    }
    
    getMessageHtml(message) {
        const bg = message.sender ? (message.is_out ? 'bg-primary text-white' : 'bg-secondary text-white') : 'bg-white text-dark border border-dark';
        const datetimeTitle = message.sender ? '' : 'Системное сообщение - '
        return `
            <div id="msg${message.id}" class="list-group-item border-0" style="width: fit-content;">
                <div class="d-flex gap-3">
                    ` + this.getAvatar(message) + `
                    <div class="${bg} rounded-3">
                        <div class="d-flex p-1 px-2" style="font-size: 18px; height: fit-content">${message.text.replaceAll('\r\n', '<br>')}</div>
                        <small class="float-end pe-1 align-self-end ps-3 mt-2" style="font-size: 11px;">${datetimeTitle}${this.formatSentAt(new Date(message.sent_at))}</small>
                    </div>  
                </div>
            </div>  
        `;
    }
    
    appendMessage(message) {      
        this.msgContainer.append(this.getMessageHtml(message));
        this.lastAppendedSenderId = message?.sender?.id;
    }

    appendExistingMessages() {
        if (window?.messages.length > 0) {
            for (var message of window.messages) {
                this.appendMessage(message);
            }
            $("html, body").scrollTop($(document).height());
        }
    }  

    sendMessage() {
        const text = this.getValue();
        if (!text) {
            return;
        }

        const formData = new FormData();
        formData.append('text', text);

        var self = this;
        self.btnSend.attr('disabled', true);
        clearInterval(self.msgTimerId);
        
        $.ajax({ 
            type: "POST",
            url: self.sendMessageApi,
            data: formData,
            processData: false,
            contentType: false,
            success: onSuccess,
            error: onError
        }); 

        
        function onSuccess(data) {
            self.textArea.val(null);

            for (let message of data.data) {
                self.appendMessage(message);
            }

            $("html, body").animate({ scrollTop: $(document).height() });
            self.msgTimerId = setInterval(self.getNewMessages, self.GET_NEW_MESSAGES_TIMER * 1000);
        }

        function onError(error) {
            showErrorToast(error.responseJSON.message);
            self.btnSend.attr('disabled', false);
        }
    }

    getNewMessages() {
        var self = this;

        $.ajax({
            type: 'GET',
            url: self.getMessagesApi,
            success: function(data) {
                if (data?.data?.length > 0) {
                    for (let message of data.data) {
                        self.appendMessage(message);
                    }
                    if (self.isOnBottom) {
                        $("html, body").animate({ scrollTop: $(document).height() });
                    } else {
                        $('#hasNewMessages').show()
                    }
                }
            }
        });
    }
    
        
}


