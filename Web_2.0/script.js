const config = {
    files: {
      "fritschi.webp": { label: "zünftig", priority: 1 },
      "hexe.webp": { label: "rüüdig", priority: 2 },
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
      "federer.webp": { label: "bönzlig", priority: 20 }
    },
    loading_time: 2000
};

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

  const labelDiv = document.createElement('div');
  labelDiv.classList.add('image-label');
  labelDiv.textContent = data.label;

  gridItem.appendChild(img);
  gridItem.appendChild(labelDiv);
  fragment.appendChild(gridItem);
});
document.querySelector('.grid-container').appendChild(fragment);

document.addEventListener('DOMContentLoaded', () => {
  // Cache frequently used elements.
  const gridContainer = document.querySelector('.grid-container');
  const squareBlock = document.querySelector('.square-block');
  const loadingScreen = document.getElementById('loadingScreen');
  const selectionScreen = document.getElementById('selectionScreen');
  const backButton = document.getElementById('backButton');
  const combinedImage = document.getElementById('combinedImage');

  let selectedItems = new Set();

    // Use event delegation on the grid container.
    gridContainer.addEventListener('click', (event) => {
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
        showLoadingScreen();
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
    selectionScreen.style.display = 'block';
  }

  backButton.addEventListener('click', () => {
    selectionScreen.style.display = 'none';
    squareBlock.style.display = 'block';
    selectedItems.clear();
    gridContainer.querySelectorAll('.grid-item').forEach(item => item.classList.remove('selected'));
  });
});
