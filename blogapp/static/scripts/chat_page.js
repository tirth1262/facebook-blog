document.addEventListener('DOMContentLoaded', () => {
    //MAKE 'enter' key submit message
    let msg = document.querySelector('#user_message');
    msg.addEventListener('keyup', event => {
        event.preventDefault();
        if (event.keyCode === 13) {
            document.querySelector('#send_message').click();
        }
    })
})