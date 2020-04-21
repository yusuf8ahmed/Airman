/*!
 * Copyright : (C) 2092  Communications Ltd Inc Corp Naruto Clan
 * Yes this real and we are a naruto clan and yes we are the true supreme leader
 * of the state of new jersey
 *
 * This JavaScript/Erlang file is the property shidded Communications Ltd Inc Corp Naruto Clan
 * and may not be copied or used/edited(get dabbed on) without prior written consent.
 *
 */

var socket = io();

console.log("Name =>",name);

socket.emit('get_friend', [name]);

socket.on('connect', function () {
    socket.emit('get_friends', name);
});

socket.on('test', function (data) {
    console.dir(data);
});

socket.on('receive_message', function (msg) {
    console.dir("Received Message", msg);

    let mess =  document.getElementById("messlist");
    let div = document.createElement('div');

    if (name === msg[0]) {
        div.innerHTML = 
            `
            <div class="d-flex justify-content-end mb-4 animated slideInUp">
                <!--
                <div class="img_cont_msg">
                    <img src="" class="rounded-circle user_img_msg">
                </div>
                -->
                <div class="msg_cotainer_send">
                    ${msg[2]}
                    <span class="msg_time_send">${new Date(msg[3]*1000).toLocaleDateString()}</span>
                </div>
            </div>
            `;            
    } else {
        div.innerHTML = 
            `
            <div class="d-flex justify-content-start mb-4 animated slideInUp">
                <!--
                    <div class="img_cont_msg">
                        <img src="https://static.turbosquid.com/Preview/001292/481/WV/_D.jpg" class="rounded-circle user_img_msg">
                    </div>
                -->
                <div class="msg_cotainer">
                    ${msg[2]}
                    <span class="msg_time">${new Date(msg[3]*1000).toLocaleDateString()}</span>
                </div>
            </div>
            `;
    }
    mess.appendChild(div);  
    ScrollDown();            
});

socket.on('receive_history', function(msg){
    console.dir("Loading in Messages",msg);

    let mess =  document.getElementById("messlist");
    csocket = msg.channel_id;

    for (let i = 0; i < msg.messages.length; i++) {
        let div = document.createElement('div');
        const k = `${new Date(msg.messages[i][2]*1000).toLocaleDateString()}`;

        if (name === msg.messages[i][0]) {
            div.innerHTML = 
                `
                <div class="d-flex justify-content-end mb-4 animated slideInUp">
                    <!--
                    <div class="img_cont_msg">
                        <img src="" class="rounded-circle user_img_msg">
                    </div>
                    -->
                    <div class="msg_cotainer_send">
                        ${msg.messages[i][3]}
                        <span class="msg_time_send">${k}</span>
                    </div>
                </div>
                `;            
        } else {
            div.innerHTML = 
                `
                <div class="d-flex justify-content-start mb-4 animated slideInUp">
                    <!--
                        <div class="img_cont_msg">
                            <img src="https://static.turbosquid.com/Preview/001292/481/WV/_D.jpg" class="rounded-circle user_img_msg">
                        </div>
                    -->
                    
                    <div class="msg_cotainer">
                        ${msg.messages[i][3]}
                        <span class="msg_time">${k}</span>
                    </div>
                </div>
                `;
        }
        mess.appendChild(div);    
        ScrollDown();            
    }
});

socket.on('friends_set', function(msg) {
    console.log("friends", msg);
    const list = document.getElementById("friendslist");
    var friend = msg[0];

    for (var i = 0; i < msg.length; i++) {
        let div = document.createElement('div');
        div.innerHTML = 
        `<button class="btn btn-primary btn-lg active btn-block mt-1 mb-1 flist" onclick="Receive(this, this.innerHTML);">${msg[i]}</button>`;
        list.appendChild(div);        
    }
});

const msg = document.getElementById("user_message");
msg.addEventListener("keyup", function(event) {
    event.preventDefault();
    if (event.keyCode === 13) {
        console.log("Send Message With Click Submit");
        document.getElementById("send_message").click();
    }
});

function ScrollDown() {
    console.log("Scrolling Down");
    const chatWindow = document.getElementById("messlist");
    chatWindow.lastChild.scrollIntoView({behavior: "smooth"});
}

function Receive(t, getname) {
    cchat = true;
    friend = getname;  
    document.getElementById("messlist").innerHTML = "";
    document.getElementsByClassName("display_message")[0].style.display = "block";
    document.getElementsByClassName("display_main")[0].style.display = "none";
    socket.emit('receive', {'main':name, 'get': friend, 'time':Math.floor(Date.now() / 1000)});
}

function Send() {
    // Send Message to Server
    const mess = document.getElementById("user_message").value;

    if (mess === ''){
        console.log("Cannot Send Empty Message");
        document.getElementById("user_message").value = 'Cannot Send empty message';
    } else {
        console.log("Sending Mesage", mess);
        const send_obj = [name, friend, mess, Math.floor(Date.now() / 1000), csocket];
        socket.emit('send_messages', send_obj);
        document.getElementById("user_message").value = '';
        console.log("Sent Message", send_obj);       
    }
}

function Home(){
    cchat = true;
    document.getElementsByClassName("display_main")[0].style.display = "block";
    document.getElementsByClassName("display_message")[0].style.display = "none";
    document.getElementById("messlist").innerHTML = "";
}