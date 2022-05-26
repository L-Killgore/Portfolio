document.addEventListener('DOMContentLoaded', function() {

    if (document.querySelector('.new-topic')) {
        document.querySelector('.new-topic').addEventListener('click', () => new_topic());
    };
    if (document.querySelector('.new-post')) {
        document.querySelector('.new-post').addEventListener('click', () => new_post());
    };
})

function new_topic() {
    let new_topic_div = document.querySelector('.new-topic-div')
    if (new_topic_div.classList.contains('d-none')) {
        new_topic_div.classList.remove('d-none');
    } else {
        new_topic_div.classList.add('d-none');
    };
}

function new_post() {
    let new_post_div = document.querySelector('.new-post-div')
    if (new_post_div.classList.contains('d-none')) {
        new_post_div.classList.remove('d-none');
    } else {
        new_post_div.classList.add('d-none');
    };
}

function commentToggle(parent_id) {
    const reply = document.getElementById(parent_id);
    let reply_content = reply.querySelector('.textarea');

    reply_content.innerHTML = '';

    if (reply.classList.contains('d-none')) {
        reply.classList.remove('d-none');
    } else {
        reply.classList.add('d-none');
    };
}