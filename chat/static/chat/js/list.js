$(document).ready(() => {
    var nextPage = 1;
    var isLoading = false;
    var hasNextPage = true;

    const $chatList = $('.chat-list');

    handleBottom();
    $(window).scroll(handleBottom);
    $(window).on('resize', handleBottom);

    function handleBottom() {
        if ($(window).scrollTop() >= $(document).height() - $(window).height() - 700) {
            loadChats();
        }
    }

    function loadChats() {
        if (isLoading || !hasNextPage) return;

        setIsLoading(true);
        $.ajax({ 
            type: "GET",
            url: '/chat/api/ajax_list/',
            data: {'page': nextPage},
            success: onSuccess,
            error: onError
        });
    
        function onSuccess(data) {
            setIsLoading(false);

            if (data?.has_next_page) {
                nextPage += 1;
            } else {
                hasNextPage = false;
            }

            for (let chat of data?.messages) {
                appendChat(chat);
            }
        }
    
        function onError() {
            setIsLoading(false);
        }
    }

    function setIsLoading(value) {
        isLoading = value;

        if (value) {
            $chatList.append(`
                <div id="isLoadingItem" class="list-group-item text-center py-3">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            `)
        } else {
            $("#isLoadingItem").remove();
        }
    }

    function appendChat(chat) {

        function _getAvatar() {
            if (chat?.sender?.avatar_sm) {
                return `<img height="32" width="32" src="${ chat.sender.avatar_sm }" class="rounded-circle of-cover">`
            }
            if (chat?.sender === null) {
                return `<img height="32" width="32" src="${ window.systemImgURL }" class="rounded-circle of-cover">`
            }
            return '<div style="width:32px; height:32px; min-width: 32px !important; min-height: 32px;"></div>'
        }

        function _getSentAt() {
            return formatDateTime(new Date(chat.sent_at), 'dd mmms yyyy, HH:MM');
        }

        function _getNewMessagesBadge() {
            if (!chat.read && chat?.recipient?.id === window.myId) {
                return `<span class="position-absolute translate-middle-y top-50 start-m14 p-1 bg-danger border border-light rounded-circle" title="Новое сообщение"></span>`;
            }
            return '';
        }

        function _getUserLabel() {
            if (!chat?.sender) {
                return ''
            }
            if (chat?.sender.id === window.myId) {
                return 'Вы: '
            }
            return `${chat?.sender?.first_name}: `
        }

        $chatList.append(`
            <a class="list-group-item py-3" href="${ chat.get_href }?back=${ window.location.pathname }">
                <div class="d-flex gap-3">
                    ${ _getAvatar() }
                    <div class="w-100">
                        <div>
                            <div class="col float-end text-muted position-relative">
                                ${ _getSentAt() } 
                                ${ _getNewMessagesBadge() }
                            </div>
                            <div class="fw-bold">${ chat?.get_title }</div>
                        </div>
                        <div>
                            <div class="col float-end">
                                ${ chat?.badge }
                            </div>   
                            <div class="mb-0 text-muted" style="max-height: 150px;">
                                ${ _getUserLabel() }
                                ${ chat?.text }
                            </div>                   
                        </div>                
                    </div>
                </div>
            </a>
        `);
    }
})