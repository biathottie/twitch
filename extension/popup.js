var checkbox = document.getElementById("myToggle")
var userList = document.getElementById("userList")
var channelPoints = document.getElementById("pointsToUse")
var ev = document.getElementById("evToUse")

var userListFinal
var channelPointsFinal
var evFinal

var autoBet = false

document.addEventListener('DOMContentLoaded', () => {
    chrome.storage.local.get(['userListFinal', 'channelPointsFinal', 'evFinal'], (result) => {
        if (result.userListFinal) {
            document.getElementById('userList').value = result.userListFinal;
        }
        if (result.channelPointsFinal) {
            document.getElementById('pointsToUse').value = result.channelPointsFinal;
        }
        if (result.evFinal) {
            document.getElementById('evToUse').value = result.evFinal;
        }
        console.log('Settings loaded!')
    });
});

checkbox.addEventListener("change", (event) => {
    if (event.currentTarget.checked) {
        chrome.storage.local.set({
            userListFinal,
            channelPointsFinal,
            evFinal
        }, () => {
            console.log('Settings saved!');
        });
        autoBet = true;
    } else {
        autoBet = false;
    }
})

userList.addEventListener("input", () => {
    const userListValue = userList.value;
    userListFinal = userListValue;
})

channelPoints.addEventListener("input", () => {
    const channelPointsValue = channelPoints.value;
    channelPointsFinal = channelPointsValue;
})

ev.addEventListener("input", () => {
    const evValue = ev.value;
    evFinal = evValue;
})