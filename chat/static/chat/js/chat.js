class MessageHandler {

    constructor(longPollingApi, sendMessageApi) {
        this.msgContainer = $('#msgContainer');
        this.btnSend = $('#btnSendMessage');
        this.textArea = $('#textArea');

        this.isOnBottom = false;
        this.longPollingApi = longPollingApi;
        this.sendMessageApi = sendMessageApi;

        var self = this;
        $(window).scroll(function() {
            self.isOnBottom = ($(window).scrollTop() + $(window).height() == $(document).height());
        });

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
        this.getNewMessages();
    };

    getValue() {
        return this.textArea.val();
    }

    getAvatar(message) {
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
    
    formatSentAt(dt) {
        return `${('0' + dt.getDate()).slice(-2)}.${('0' + (dt.getMonth() + 1)).slice(-2)}.${dt.getFullYear()}, ${('0' + dt.getHours()).slice(-2)}:${('0'+dt.getMinutes()).slice(-2)}`;
    }
    
    getMessageHtml(message) {
        const bg = message.sender ? (message.is_out ? 'bg-primary text-white' : 'bg-secondary text-white') : 'bg-white text-dark border border-dark';
        const datetimeTitle = message.sender ? '' : 'Системное сообщение<br>'
        return `
            <div id="msg${message.id}" class="list-group-item border-0" style="width: fit-content;">
                <div class="d-flex gap-3">
                    ` + this.getAvatar(message) + `
                    <div class="d-flex ${bg} rounded p-1 px-2" style="font-size: 18px; height: fit-content">${message.text.replaceAll('\r\n', '<br>')}</div>
                    <small class="float-end pe-1 align-self-end" style="font-size: 12px;">${datetimeTitle}${this.formatSentAt(new Date(message.sent_at))}</small>
                </div>
            </div>  
        `;
    }
    
    appendMessage(message) {      
        this.msgContainer.append(this.getMessageHtml(message));
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
            self.appendMessage(data.data);
            $("html, body").animate({ scrollTop: $(document).height() });
        }

        function onError(error) {
            showErrorToast(error.responseJSON.message);
        }
    }

    // Long polling
    getNewMessages() {
        var self = this;
        $.ajax({
            type: 'GET',
            url: this.longPollingApi,
        }).done(function(data) {
            if (data?.data?.length > 0) {
                for (let message of data.data) {
                    self.appendMessage(message);
                }
                if (self.isOnBottom) {
                    $("html, body").animate({ scrollTop: $(document).height() });
                }
            }
            self.getNewMessages();
        }).fail(function(error) {
            if (error.status == 0) {
                self.getNewMessages();
            }
        })
    }
    
        
}


