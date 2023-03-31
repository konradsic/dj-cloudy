// Handle joining vc - then bot will start playing
var djCloudy = document.getElementById("dj-cloudy");
var djCloudyImg = document.getElementById("dj-cloudy-img");
var vcUser = document.getElementById("you");
var friends = document.getElementsByClassName("friend");

var channel = document.querySelector(".discord-vc");
var leaveBtn = document.querySelector(".leave-btn");
var gotItBox = document.getElementById("got-it");
var lookBox = document.querySelector(".gradient-box-look");

const joinChannel = () => {
    vcUser.classList.remove("hidden");
}

const leaveChannel = () => {
    vcUser.classList.add("hidden");
}
const djPlay = state => {
    if (state) 
        djCloudy.classList.add("speaking");
    else
        djCloudy.classList.remove("speaking");
}

const showLeaveBtn = () => {
    leaveBtn.classList.remove("hidden");
}
const hideLeaveBtn = () => {
    leaveBtn.classList.add("hidden");
}

channel.onclick = () => {
    joinChannel();
    djPlay(true);
    showLeaveBtn();
}

leaveBtn.onclick = () => {
    leaveChannel();
    djPlay(false);
    hideLeaveBtn();
}

gotItBox.onclick = () => {
    lookBox.classList.add("hidden");
}