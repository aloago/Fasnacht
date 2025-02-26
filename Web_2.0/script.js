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
    back_button_delay: 100, // Delay after back button is pressed (in milliseconds)
    selection_delay: 250, // Delay after a selection is made (in milliseconds)
  };
  
make_pressable(document.querySelector('.back-button'));

// Build the grid using Object.entries to iterate over the files.
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

// Function to add 'pressed' class
function addPressedClass(event) {
event.target.classList.add('pressed');
}

// Function to remove 'pressed' class
function removePressedClass(event) {
event.target.classList.remove('pressed');
}

function make_pressable(element) {
element.classList.add('scale-on-touch');
element.addEventListener('touchstart', addPressedClass);
element.addEventListener('touchend', removePressedClass);
element.addEventListener('touchcancel', removePressedClass);
element.addEventListener('mousedown', addPressedClass); // For mouse click
element.addEventListener('mouseup', removePressedClass); // For mouse release
element.addEventListener('mouseleave', removePressedClass); // In case the mouse leaves the button
}

document.addEventListener('DOMContentLoaded', () => {
// Cache frequently used elements.
const gridContainer = document.querySelector('.grid-container');
const squareBlock = document.querySelector('.square-block');
const loadingScreen = document.getElementById('loadingScreen');
const selectionScreen = document.getElementById('selectionScreen');
const backButton = document.getElementById('backButton');
const combinedImage = document.getElementById('combinedImage');

let selectedItems = new Set();
let selectionDisabled = false; // Flag to disable selection during delay

// Use event delegation on the grid container.
gridContainer.addEventListener('click', (event) => {
    if (selectionDisabled) return; // If selection is disabled, do nothing

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
    selectionDisabled = true; // Disable further selection
    // Delay before showing the loading screen
    setTimeout(() => {
        showLoadingScreen();
    }, config.selection_delay); // Adjust the delay time (in milliseconds) as needed
    }
});

function showLoadingScreen() {
    squareBlock.style.display = 'none';
    loadingScreen.style.display = 'block';

    setTimeout(() => {
    loadingScreen.style.display = 'none';
    showSelectionScreen();
    }, config.loading_time);
}

function showSelectionScreen() {
    // Sort the selected items based on their priority.
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
    selectionScreen.style.display = 'none';
    squareBlock.style.display = 'block';
    selectedItems.clear();
    gridContainer.querySelectorAll('.grid-item').forEach(item => item.classList.remove('selected'));
    selectionDisabled = false; // Re-enable selection after returning
    }, config.back_button_delay); // Delay before returning to selection screen
});
});
