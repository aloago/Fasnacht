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
        }, 2000);
    }

    function showSelectionScreen() {
        const sortedFilenames = Array.from(selectedItems).sort((a, b) => {
            const aPriority = parseInt(document.querySelector(`[data-filename="${a}"]`).dataset.priority);
            const bPriority = parseInt(document.querySelector(`[data-filename="${b}"]`).dataset.priority);
            return aPriority - bPriority;
        });

        const combinedName = `${sortedFilenames[0].split('.')[0]}-${sortedFilenames[1].split('.')[0]}.jpg`;
        combinedImage.src = `/static/Images/Selections/${combinedName}`;
        
        selectionScreen.style.display = 'block';
    }

    backButton.addEventListener('click', () => {
        selectionScreen.style.display = 'none';
        document.querySelector('.square-block').style.display = 'block';
        selectedItems.clear();
        gridItems.forEach(item => item.classList.remove('selected'));
    });
});