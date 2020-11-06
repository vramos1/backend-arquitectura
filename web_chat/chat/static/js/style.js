const container = document.getElementById('chat-view');

if (container) {
    container.scrollTo(0, container.scrollHeight);
}

function redirect(element) {
    if (element.value) {
        window.location = '/' + element.value;
    } else {
        window.location = '/'
    }
}