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
    dropZone.style.border = "2px dashed #ccc";

    const droppedFile = e.dataTransfer.files[0];
    readAndResizeFile(droppedFile);
});


dropZone.addEventListener("click", () => {
    fileInput.click();
});

fileInput.addEventListener("change", () => {
    const selectedFile = fileInput.files[0];
    readAndResizeFile(selectedFile);
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
    if (file && file.type.startsWith("image/")) {
        const reader = new FileReader();

        reader.onload = function () {
            const img = new Image();
            img.src = reader.result;

            img.onload = function () {

                var resizedDataURL = resizeImage(img, file.type);

                imageElement.src = resizedDataURL;
                imageElement.style.display = "block";

                cropper = new Cropper(imageElement, {
                    //TODO remove transparent background
                    data:{
                        width: 450
                    },
                });
            };
        };

        reader.readAsDataURL(file);

        dropZone.style.display = "none";
    }
}

function resetDropZone() {
    imageElement.src = "";
    dropZone.style.display = "block";
    cropper.destroy();
}