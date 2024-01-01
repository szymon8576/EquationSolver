const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d", { willReadFrequently: true });
ctx.fillStyle = "rgb(255,255,255)";
ctx.fillRect(0, 0, canvas.width, canvas.height);

const clearButton = document.getElementById("clearButton");
const solveButton = document.getElementById("solveButton");
const solutionDiv = document.getElementById("solution");

solveButton.addEventListener("click", () => {
    solveButton.disabled = true;
    setTimeout(() => {
        solveButton.disabled = false;
    }, 3000);
});

let drawing = false;
let lastX = 0;
let lastY = 0;

// Mouse Event Listeners
canvas.addEventListener("mousedown", (e) => {
    drawing = true;
    setLastCoordinates(e.clientX, e.clientY);
});

canvas.addEventListener("mouseup", () => {
    drawing = false;
    ctx.beginPath();
});

canvas.addEventListener("mousemove", (e) => {
    if (!drawing) return;
    draw(e.clientX, e.clientY);
});

canvas.addEventListener("mouseleave", () => {
    drawing = false;
    ctx.beginPath();
});

// Touch Event Listeners
canvas.addEventListener("touchstart", (e) => {
    e.preventDefault();
    setLastCoordinates(e.touches[0].clientX, e.touches[0].clientY);
    drawing = true;
});

canvas.addEventListener("touchend", () => {
    drawing = false;
    ctx.beginPath();
});

canvas.addEventListener("touchmove", (e) => {
    if (!drawing) return;
    e.preventDefault();
    draw(e.touches[0].clientX, e.touches[0].clientY);
});

clearButton.addEventListener("click", clearInput);
solveButton.addEventListener("click", solveEquation);

function setLastCoordinates(x, y) {
    lastX = x - canvas.getBoundingClientRect().left;
    lastY = y - canvas.getBoundingClientRect().top;
}

function draw(x, y) {
    ctx.lineWidth = 4;
    ctx.lineCap = "round";
    ctx.strokeStyle = "black";

    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(x - canvas.getBoundingClientRect().left, y - canvas.getBoundingClientRect().top);
    ctx.stroke();

    setLastCoordinates(x, y);
}

function clearInput() {
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    resetDropZone();
    scroll_to_input_div();
}
