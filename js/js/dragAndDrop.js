const dropZone = document.getElementById("dropZone");
const imageElement = document.getElementById("imagePlaceholder");
const fileInput = document.getElementById("fileInput");




dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.style.border = "2px dashed #007BFF";
});

dropZone.addEventListener("dragleave", () => {
    dropZone.style.border = "2px dashed #ccc";
});


dropZone.addEventListener("drop", (e) => {
    e.preventDefault();

    if(fileInput.files.length == 1 && fileInput.files[0].type == "image/png")
    {
        dropZone.style.border = "2px dashed #ccc";
        readAndResizeFile(e.dataTransfer.files[0]);
    }
});


dropZone.addEventListener("click", () => {
    fileInput.click();
});

fileInput.addEventListener("change", () => {
    if(fileInput.files.length == 1 && fileInput.files[0].type == "image/png") 
    {
        readAndResizeFile(fileInput.files[0]);
    }
});


function resizeImage(img, fileType, maxWidth = 500){
    const resizing_canvas = document.createElement("canvas");
    const resizing_ctx = resizing_canvas.getContext("2d");

    let newWidth = img.width;
    let newHeight = img.height;

    
    const scaleFactor = maxWidth / newWidth;
    newWidth *= scaleFactor;
    newHeight *= scaleFactor;
    

    resizing_canvas.width = newWidth;
    resizing_canvas.height = newHeight;
    resizing_ctx.drawImage(img, 0, 0, newWidth, newHeight);

    return resizing_canvas.toDataURL(fileType);
}

let cropper;

function readAndResizeFile(file) {
        const reader = new FileReader();

        reader.onload = function () {
            const img = new Image();
            img.src = reader.result;

            img.onload = function () {

                var resizedDataURL = resizeImage(img, file.type);

                imageElement.src = resizedDataURL;
                imageElement.style.display = "block";

                cropper = new Cropper(imageElement, {
                    data:{
                        width: 450
                    },
                });
            };
        };

        reader.readAsDataURL(file);

        dropZone.style.display = "none";
}

function resetDropZone() {
    imageElement.src = "";
    dropZone.style.display = "block";
    if(cropper) cropper.destroy();
}