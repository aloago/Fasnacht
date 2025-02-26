const config = {
    files: {
        "fritschi.webp": { label: "zünftig", priority: 1 },
        "hexe.webp": { label: "rüüdig", priority: 2 },
        "spoerri.webp": { label: "kult-urig", priority: 3 },
        "basler.webp": { label: "appropriated", priority: 4 },
        "fisch.webp": { label: "laborig", priority: 13 },
        "affe.webp": { label: "huereaffig", priority: 6 },
        "sau.webp": { label: "sauglatt", priority: 7 },
        "krieger.webp": { label: "kriegerisch", priority: 8 },
        "clown.webp": { label: "creepy", priority: 9 },
        "hase.webp": { label: "cute", priority: 10 },
        "einhorn.png": { label: "magisch", priority: 11 },
        "grinch.webp": { label: "cringe", priority: 17 },
        "alien.webp": { label: "extraterrestrisch", priority: 5 },
        "teufel.webp": { label: "teuflisch", priority: 14 },
        "guy.webp": { label: "random", priority: 15 },
        "ueli.webp": { label: "schwurblig", priority: 16 },
        "steampunk.webp": { label: "boomerig", priority: 12 },
        "pippi.webp": { label: "feministisch", priority: 18 },
        "wonderwoman.webp": { label: "superstark", priority: 19 },
        "federer.webp": { label: "bönzlig", priority: 20 }
    },
    loading_time: 1000,
    back_button_delay: 100,
    selection_delay: 250,
};

const socket = new WebSocket('ws://localhost:8765');

const gpioFiles = [
    "spoerri-fisch.webp",
    "sau-wonderwoman.webp",
    "krieger-grinch.webp",
    "affe-pippi.webp",
    "fritschi-clown.webp",
    "hexe-basler.webp",
    "alien-hase.webp"
];

// Cache frequently used elements
const gridContainer = document.querySelector('.grid-container');
const squareBlock = document.querySelector('.square-block');
const loadingScreen = document.getElementById('loadingScreen');
const selectionScreen = document.getElementById('selectionScreen');
const backButton = document.getElementById('backButton');
const combinedImage = document.getElementById('combinedImage');

let selectedItems = new Set();
let selectionDisabled = false;

// Function to show a random file from the list
function showGpioLockScreen() {
    const randomFile = gpioFiles[Math.floor(Math.random() * gpioFiles.length)];
    combinedImage.src = `Images/Selections/${randomFile}`;
    selectionScreen.style.display = 'block';
    backButton.style.display = 'none'; // Hide the back button
}

// Function to return to the grid and reset the selection state
function returnToGrid() {
    // Reset the selection grid state
    selectedItems.clear(); // Clear the selected items
    gridContainer.querySelectorAll('.grid-item').forEach(item => {
        item.classList.remove('selected'); // Remove the selected class
    });
    selectionDisabled = false; // Re-enable selection

    // Show the grid and hide the selection screen
    selectionScreen.style.display = 'none';
    squareBlock.style.display = 'block';
    backButton.style.display = 'block'; // Show the back button
}

// Handle WebSocket messages
socket.addEventListener('message', (event) => {
    const gpioState = event.data === 'True'; // Convert string to boolean

    if (!gpioState) {
        // GPIO is low: show a random file and lock the screen
        showGpioLockScreen();
    } else {
        // GPIO is high: return to the grid and reset the selection state
        returnToGrid();
    }
});

// Handle WebSocket errors
socket.addEventListener('error', (error) => {
    console.error('WebSocket error:', error);
});

// Handle WebSocket close
socket.addEventListener('close', () => {
    console.warn('WebSocket connection closed');
});

// Existing grid item click handler
gridContainer.addEventListener('click', (event) => {
    if (selectionDisabled) return;

    const item = event.target.closest('.grid-item');
    if (!item) return;

    const filename = item.dataset.filename;
    if (selectedItems.has(filename)) {
        selectedItems.delete(filename);
        item.classList.remove('selected');
    } else if (selectedItems.size < 2) {
        selectedItems.add(filename);
        item.classList.add('selected');
    }

    if (selectedItems.size === 2) {
        selectionDisabled = true;
        setTimeout(() => {
            showLoadingScreen();
        }, config.selection_delay);
    }
});

// Existing functions
function showLoadingScreen() {
    squareBlock.style.display = 'none';
    loadingScreen.style.display = 'block';

    setTimeout(() => {
        loadingScreen.style.display = 'none';
        showSelectionScreen();
    }, config.loading_time);
}

function showSelectionScreen() {
    const sortedItems = Array.from(selectedItems)
        .map(filename => ({ filename, ...config.files[filename] }))
        .sort((a, b) => a.priority - b.priority);

    const combinedName = `${sortedItems[0].filename.split('.')[0]}-${sortedItems[1].filename.split('.')[0]}.webp`;
    combinedImage.src = `Images/Selections/${combinedName}`;
    combinedImage.draggable = false;
    selectionScreen.style.display = 'block';
}

backButton.addEventListener('click', () => {
    setTimeout(() => {
        returnToGrid(); // Use the same function to reset the grid state
    }, config.back_button_delay);
});

// Build the grid
const fragment = document.createDocumentFragment();
Object.entries(config.files).forEach(([filename, data]) => {
    const gridItem = document.createElement('div');
    gridItem.classList.add('grid-item');
    gridItem.dataset.filename = filename;
    gridItem.dataset.priority = data.priority;

    const img = document.createElement('img');
    img.src = `Images/Grid/${filename}`;
    img.alt = data.label;
    img.draggable = false;
    make_pressable(img);

    const labelDiv = document.createElement('div');
    labelDiv.classList.add('image-label');
    labelDiv.textContent = data.label;

    gridItem.appendChild(img);
    gridItem.appendChild(labelDiv);
    fragment.appendChild(gridItem);
});
document.querySelector('.grid-container').appendChild(fragment);

// Existing make_pressable function
function make_pressable(element) {
    element.classList.add('scale-on-touch');
    element.addEventListener('touchstart', addPressedClass);
    element.addEventListener('touchend', removePressedClass);
    element.addEventListener('touchcancel', removePressedClass);
    element.addEventListener('mousedown', addPressedClass);
    element.addEventListener('mouseup', removePressedClass);
    element.addEventListener('mouseleave', removePressedClass);
}

// Existing pressed class functions
function addPressedClass(event) {
    event.target.classList.add('pressed');
}

function removePressedClass(event) {
    event.target.classList.remove('pressed');
}