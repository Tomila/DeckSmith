document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('shoeModal');
    const closeButton = document.querySelector('.modal .close');
    const modalImage = document.getElementById('modal-image');
    const modalTitle = document.getElementById('modal-title');
    const modalPrice = document.getElementById('modal-price');
    const modalDescription = document.getElementById('modal-description');

    document.querySelectorAll('.view-details').forEach(button => {
        button.addEventListener('click', function() {
            // Retrieve shoe details from data attributes
            const image = this.getAttribute('data-image');
            const name = this.getAttribute('data-name');
            const price = this.getAttribute('data-price');
            const description = this.getAttribute('data-description');

            // Update modal content
            modalImage.src = image;
            modalTitle.textContent = name;
            modalPrice.textContent = `$${price}`;
            modalDescription.textContent = description;
            
            // Show the modal
            modal.style.display = 'block';
        });
    });

    closeButton.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
});


