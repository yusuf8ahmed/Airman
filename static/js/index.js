const myForm = document.forms[1];

myForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const x = document.getElementById("name").value;
    const y = document.getElementById("pass").value;
    const k = document.getElementById("error");

    if (y.length > 2) {
        // username larger than 2 char
        k.style.display = "block";
        k.innerHTML = `<p>"${x}" is too Short</p>`;
    } else if (x.length > 8) {
        // pass larger than 8 char
        k.style.display = "block";
        k.innerHTML = `<p>"${x}" is too Short</p>`;
    } else {
        const data = new FormData();
        const keys = await MakeKeys(document.getElementById("name").value, document.getElementById("mail").value);

        Download(keys[0], "PrivateKey.sec.asc", "text");

        data.append("first", document.getElementById("frist").value);
        data.append("last", document.getElementById("last").value);
        data.append("mail", document.getElementById("mail").value);
        data.append("name", document.getElementById("name").value);
        data.append("pass", document.getElementById("pass").value);
        data.append("publickey", keys[1]);

        fetch(regis, {
            method:'post',
            body: data
        });   
    }
});

MakeKeys = async(name, email)  => {
    var array = new Uint32Array(20);
    const { privateKeyArmored, publicKeyArmored, revocationCertificate } = await openpgp.generateKey({
        userIds: [{ name: name, email: email }], // you can pass multiple user IDs
        curve: 'p256',                                           // ECC curve name
        passphrase: String(window.crypto.getRandomValues(array))           // protects the private key
    });

    return [privateKeyArmored, publicKeyArmored, revocationCertificate];
}

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


function Download(data, filename, type) {
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

