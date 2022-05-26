document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('.follow_button')) {
        document.querySelector('.follow_button').addEventListener('click', async () => await follow());
    };
    if (document.querySelectorAll('.edit')) {
        document.querySelectorAll('.edit').forEach(button => button.addEventListener('click', (event) => edit(event)));
    };
    if (document.querySelectorAll('.like')) {
        document.querySelectorAll('.like').forEach(button => button.addEventListener('click', async (event) => like(event)));
    };
})


function edit(event) {
    let edit_button = event.target;
    let post = edit_button.parentNode;
    let post_content = post.querySelector('.post_content');
    const original = post_content.innerHTML;

    post_content.innerHTML = 
        `<form id="edit_form">
            <textarea class="form-control" id="edit_textarea">${original}</textarea>
            <input class="btn btn-sm btn-success submit" type="submit" value="Submit">
        </form>`;

    edit_button.disabled = true;

    document.querySelector('#edit_form').onsubmit = async (event) => {
        event.preventDefault()
        await fetch('/network/edit', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                original_post: original,
                edited_post: document.querySelector('#edit_textarea').value
            })
        })
        .then(post_content.innerHTML = document.querySelector('#edit_textarea').value)
        .then(edit_button.disabled = false);
    };
}


async function follow() {
    let follow_button = document.querySelector('.follow_button');
    let followed_user = document.querySelector('.username').innerHTML;
    let followed_number = document.querySelector('.followed_by');
    let follow_sp = document.querySelector('.follow_sp');

    // Fetch to follow profile_user
    await fetch(`/network/follow/${followed_user}`)
    .then(response => response.json())
    .then(button_state => {
        // Switch value of follow button on click
        if (button_state == true) {
            followed_number.innerHTML++;
            follow_button.innerHTML = 'Unfollow';
        } else {
            followed_number.innerHTML--;
            follow_button.innerHTML = 'Follow';
        };

        // switch between singular and plural
        if (followed_number.innerHTML == 1) {
            follow_sp.innerHTML = ' Follower';
        } else {
            follow_sp.innerHTML = ' Followers';
        };
    });
}


async function like(event) {
    let like_button = event.target;
    let post = like_button.parentNode;
    let post_id = post.getAttribute('name');
    let like_number = post.querySelector('.likes_number');
    let like_sp = post.querySelector('.like_sp')

    // Fetch to like post
    await fetch(`/network/like/${post_id}`)
    .then(response => response.json())
    .then(button_state => {
        // Switch value of like button on click
        if (button_state == true) {
            like_number.innerHTML++;
            like_button.innerHTML = 'Unlike';
        } else {
            like_number.innerHTML--;
            like_button.innerHTML = 'Like';
        };

        // switch between singular and plural
        if (like_number.innerHTML == 1) {
            like_sp.innerHTML = ' Like';
        } else {
            like_sp.innerHTML = ' Likes';
        };
    });
}