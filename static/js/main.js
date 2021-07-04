let subLen = 0;
let img = null;
let resultImage = null;
let filename="";
function fileValidate() {
    var fileInput = document.getElementById("file-input");
    console.log(fileInput);
    var filePath = fileInput.value;
    console.log(filePath);
    var allowedExtensions = /(\.jpg|\.jpeg|\.png|)$/i;
    var image1 = /\.jpg$/i;
    var image2 = /\.jpeg$/i;
    var image3 = /\.png$/i;
    if (!allowedExtensions.exec(filePath)) {
        alert("Please try another image with format png, jpg, jpeg");
        fileInput.value = "";
        return false;
    } else {
        if (fileInput.files && fileInput.files[0]) {
            var reader = new FileReader();
            reader.onload = function (e) {
                img = e.target.result;
                console.log(e.target.result);
            }
            reader.readAsDataURL(fileInput.files[0]);
            if (image1.exec(filePath)) {
                console.log("jpg");
                subLen = 23
            } else if (image2.exec(filePath)) {
                console.log("jpeg");
                subLen = 23;
            } else if (image3.exec(filePath)) {
                console.log("png");
                subLen = 22;
            }
        }
    }
}

async function watermarkImage() {

    if (img == null) {
        alert("You must upload the image");
        return;
    }
    console.log('water marking image')
    console.log('signature ' + document.getElementById('signature').textContent);

    if (document.getElementById('signature').textContent === '') {
        alert('You must log in to watermark the image!');
        return;
    }
    var signature = document.getElementById('signature').textContent;

    if (signature.length != 25) {
        alert("signature length must be 25 character");
    } else {
        $('.loading').show();
        await fetch('/watermark', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                base64: img.slice(subLen).toString(),
                signature: signature.toString(),
            })
        })
            .then(response => response.json())
            .then(data => {
                $('.loading').hide();
                console.log(data);
                if (data.result == 'Image was had sign') {
                    alert('Image already had a sign. Please try another');
                    return;
                }
                resultImage = data.result;
                displayResultImage();
                document.getElementById('result').innerHTML ="Signature is : ";
            });
    }
}

function displayResultImage() {
    if (resultImage != null) {
        document.getElementById('result-image').setAttribute('src', resultImage);
        document.getElementById('file-out-put-content').style.display = 'block';
        document.getElementById('output-image-placeholder').style.display = 'none';
        console.log('result image: ' + resultImage);
        console.log('updated result image');
    }
}
function saveImage( ) {
    let link = document.createElement("a");
    let filenames=filename+"_watermark";
    document.body.appendChild(link); // for Firefox

    link.setAttribute("href", resultImage);
    console.log(filenames);
    link.setAttribute("download", filenames);
    link.click();
}

function readURL(input) {
    fileValidate();
    if (input.files && input.files[0]) {

        var reader = new FileReader();

        reader.onload = function (e) {
            $('.image-upload-wrap').hide();

            $('.file-upload-image').attr('src', e.target.result);
            $('.file-upload-content').show();

            $('.image-title').html(input.files[0].name);
            filename=input.files[0].name;
            filename=filename.substring(0,filename.lastIndexOf('.'));
            console.log(filename);

        };;
        reader.readAsDataURL(input.files[0]);

    } else {
        removeUpload();
    }
}

async function getSignatureFromImage() {
    if (img == null) {
        alert("You must upload the image");
        return;
    } else {
        $('.loading').show();
        await fetch('/signature', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                base64: img.slice(subLen).toString()
            })
        })
            .then(function (response) {
                $('.loading').hide();
                if (response.ok) {
                    response.json().then(data => {
                        console.log('your signature is  ' + data.result);
                        document.getElementById('result').innerHTML ="Signature is : "+ data.result
                    });
                } else {
                    alert("This image doesn't have signature.");
                }
            })
    }
}


function readURLout(input) {
    var reader = new FileReader();

    reader.onload = function (e) {
        $('.image-output-wrap').hide();

        $('.file-output-image').attr('src', e.target.result);
        $('.file-output-content').show();

        $('.image-title-out').html(input.files[0].name);
    };

    reader.readAsDataURL(input.files[0]);
}

function watermarking() {

}
function unwatermarking() {

}

function removeUpload() {
    $('.file-upload-input').replaceWith($('.file-upload-input').clone());
    $('.file-upload-content').hide();
    $('.image-upload-wrap').show();
    $('.file-upload-input').val("");
    img=null;
    document.getElementById('result').innerHTML ="Signature is : ";
}

$('.image-upload-wrap').bind('dragover', function () {
    $('.image-upload-wrap').addClass('image-dropping');
});

$('.image-upload-wrap').bind('dragleave', function () {
    $('.image-upload-wrap').removeClass('image-dropping');
});

function removeOutput(){
    $('.file-output-content').hide();
    $('.image-output-wrap').show();
}

function checkLogIn() {
    let isLogIn = true;
    if (document.getElementById('signature') == null) {
        isLogIn = false;
    }
    if (isLogIn) {
        document.getElementById('login-button').style.display = 'none';
        document.getElementById('signup-button').style.display = 'none';
        document.getElementById('logout-button').style.display = 'inline';
    } else {
        document.getElementById('login-button').style.display = 'inline';
        document.getElementById('signup-button').style.display = 'inline';
        document.getElementById('logout-button').style.display = 'none';
    }
}