const config = {
    "file_names": ["fritschi.webp", "hexe.webp", "spoerri.webp", "basler.webp", "fisch.webp", 
                "affe.webp", "sau.webp", "krieger.webp", "clown.webp", "hase.webp", 
                "einhorn.png", "grinch.webp", "alien.webp", "teufel.webp", "guy.webp", 
                "ueli.webp", "steampunk.webp", "pippi.webp", "wonderwoman.webp", "federer.webp"],
    "labels": ["zünftig", "rüüdig", "kult-urig", "appropriated", "laborig", 
            "huereaffig", "sauglatt", "kriegerisch", "creepy", "cute", 
            "magisch", "cringe", "extraterrestrisch", "teuflisch", "random", 
            "schwurblig", "boomerig", "feministisch", "superstark", "bönzlig"],
    "priority_list": [1, 2, 3, 4, 13, 6, 7, 8, 9, 10, 11, 17, 5, 14, 15, 16, 12, 18, 19, 20],
    "loading_time": 2000
}

for (let i = 0; i < 20; i++) {
    document.querySelector('.grid-container').innerHTML += `
    <div class="grid-item" data-filename="${config["file_names"][i]}" data-priority="${config["priority_list"][i]}">
            <img src="Images/Grid/${config["file_names"][i]}" 
                    alt="${config["labels"][i]}">
            <div class="image-label">${config["labels"][i]}</div>
        </div>
    `
}

document.addEventListener('DOMContentLoaded', () => {
    const gridItems = document.querySelectorAll('.grid-item');
    const loadingScreen = document.getElementById('loadingScreen');
    const selectionScreen = document.getElementById('selectionScreen');
    const backButton = document.getElementById('backButton');
    const combinedImage = document.getElementById('combinedImage');
    
    let selectedItems = new Set();

    gridItems.forEach(item => {
        item.addEventListener('click', () => {
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
    });

    function showLoadingScreen() {
        document.querySelector('.square-block').style.display = 'none';
        loadingScreen.style.display = 'block';
        
        setTimeout(() => {
            loadingScreen.style.display = 'none';
            showSelectionScreen();
        }, config["loading_time"]);
    }

    function showSelectionScreen() {
        const sortedFilenames = Array.from(selectedItems).sort((a, b) => {
            const aPriority = parseInt(document.querySelector(`[data-filename="${a}"]`).dataset.priority);
            const bPriority = parseInt(document.querySelector(`[data-filename="${b}"]`).dataset.priority);
            return aPriority - bPriority;
        });

        const combinedName = `${sortedFilenames[0].split('.')[0]}-${sortedFilenames[1].split('.')[0]}.webp`;
        combinedImage.src = `Images/Selections/${combinedName}`;
        
        selectionScreen.style.display = 'block';
    }

    backButton.addEventListener('click', () => {
        selectionScreen.style.display = 'none';
        document.querySelector('.square-block').style.display = 'block';
        selectedItems.clear();
        gridItems.forEach(item => item.classList.remove('selected'));
    });
});