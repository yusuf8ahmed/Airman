function ShowLogin() {
    document.getElementsByClassName("main")[0].style.display = "none";
    document.getElementsByClassName("regis")[0].style.display = "none";
    document.getElementsByClassName("login")[0].style.display = "block";
}

function ShowRegis() {
    document.getElementsByClassName("main")[0].style.display = "none";
    document.getElementsByClassName("login")[0].style.display = "none";
    document.getElementsByClassName("regis")[0].style.display = "block";
}

function ShowMain() {
    document.getElementsByClassName("login")[0].style.display = "none";
    document.getElementsByClassName("regis")[0].style.display = "none";
    document.getElementsByClassName("main")[0].style.display = "block";
}

function ValidateForm() {
    var x = document.getElementById("name").value;
    var y = document.getElementById("pass").value;
    var k = document.getElementById("error");

    if (x.lenght > 2) {
        // username larger than 2 char
        let r = "Username is too Short";
        k.style.display = "block";
        k.innerHTML = `<p>$(r)</p>`;
        return false;
    } else if (x.lenght > 8) {
        // pass larger than 8 char
        const k = "Password is too Short";
        k.style.display = "block";
        k.innerHTML = `<p>$(r)</p>`;
        return false;
    } else {
        return true;
    }
    
}

function download(data, filename, type) {
    let file = new Blob([data], {type: type});
    if (window.navigator.msSaveOrOpenBlob) // IE10+
        window.navigator.msSaveOrOpenBlob(file, filename);
    else { // Others
        var a = document.createElement("a");
        var url = URL.createObjectURL(file);
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        setTimeout(function() {
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);  
        }, 0); 
    }
}

