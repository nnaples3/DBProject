// Simple JS to confirm it's loading
console.log("index.js loaded!");

// Example: Alert on button click
document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll("button");
    buttons.forEach((btn) => {
        btn.addEventListener("click", () => {
            alert("Button clicked!");
        });
    });
});