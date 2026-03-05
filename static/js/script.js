function setWear(min, max) {
  document.getElementById('min_float').value = min;
  document.getElementById('max_float').value = max;
}

document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('itemModal');
  if (!modal) return;

  // =========================================================
  // 1. STAR RATING LOGIC (Strictly isolated to the form!)
  // =========================================================
  // Notice we added #commentForm to the query so it ONLY gets the 5 modal stars
  const formStars = document.querySelectorAll('#commentForm .js-star');
  const ratingInput = document.getElementById('hiddenRatingInput');

  if (formStars.length > 0 && ratingInput) {
    formStars.forEach(star => {
      // Using onclick guarantees only one click listener ever exists
      star.onclick = function (e) {
        const clickedRating = parseInt(this.dataset.value);
        const currentSavedRating = parseInt(ratingInput.value);

        // Toggle logic
        if (clickedRating === currentSavedRating) {
          ratingInput.value = 0; // Reset
          formStars.forEach(s => {
            s.classList.remove('text-yellow-400');
            s.classList.add('text-gray-400');
          });
        } else {
          ratingInput.value = clickedRating; // Set new rating
          formStars.forEach(s => {
            const starVal = parseInt(s.dataset.value);
            if (starVal <= clickedRating) {
              s.classList.remove('text-gray-400');
              s.classList.add('text-yellow-400');
            } else {
              s.classList.remove('text-yellow-400');
              s.classList.add('text-gray-400');
            }
          });
        }
      };
    });
  }

  // =========================================================
  // 2. MODAL OPEN LOGIC
  // =========================================================
  document.body.addEventListener('click', e => {
    const card = e.target.closest('.js-skin-card');

    if (card) {
      const data = card.dataset;

      // Populate modal details
      document.getElementById('modalItemId').textContent =
        'Item id #' + data.id;
      document.getElementById('modalName').textContent = data.name;
      document.getElementById('modalPrice').textContent = data.price + '€';
      document.getElementById('modalWear').textContent = data.wear;
      document.getElementById('modalRarity').textContent = data.rarity;

      const imgElement = document.getElementById('modalImage');
      imgElement.src = data.image;
      imgElement.alt = data.name;

      document.getElementById('modalFloat').textContent = data.float;
      document.getElementById('modalSeed').textContent = data.seed;

      const patternContainer = document.getElementById('modalPatternContainer');
      if (data.pattern && data.pattern !== 'None' && data.pattern !== '') {
        document.getElementById('modalPattern').textContent = data.pattern;
        patternContainer.classList.remove('hidden');
        patternContainer.classList.add('flex');
      } else {
        patternContainer.classList.add('hidden');
        patternContainer.classList.remove('flex');
      }

      const statTrakBadge = document.getElementById('modalStatTrak');
      if (data.stattrak === 'True' || data.stattrak === 'true') {
        statTrakBadge.classList.remove('hidden');
        statTrakBadge.classList.add('block');
      } else {
        statTrakBadge.classList.add('hidden');
        statTrakBadge.classList.remove('block');
      }

      window.currentSelectedItemId = data.id;

      const inCart = data.incart === 'true';
      const addToCartForm = document.getElementById('modalAddToCartForm');
      const addToCartBtn = document.getElementById('modalAddToCartBtn');
      const commentsList = document.getElementById('modalCommentsList');

      if (addToCartForm && addToCartBtn) {
        if (inCart) {
          addToCartForm.action = '';
          addToCartBtn.disabled = true;
          addToCartBtn.textContent = 'In Cart';
          addToCartBtn.className =
            'w-full bg-gray-600 text-gray-400 py-2 rounded-btn font-bold cursor-not-allowed';
        } else {
          addToCartForm.action = '/add_to_cart/' + data.id;
          addToCartBtn.disabled = false;
          addToCartBtn.textContent = 'Add to Cart';
          addToCartBtn.className =
            'w-full bg-accent text-gray-900 py-2 rounded-btn font-bold hover:bg-accent-hover transition-colors';
        }
      }

      // --- RESET THE MODAL STARS ONLY ---
      const activeRatingInput = document.getElementById('hiddenRatingInput');
      const activeFormStars = document.querySelectorAll(
        '#commentForm .js-star',
      );

      if (activeRatingInput) {
        activeRatingInput.value = 0;
      }
      if (activeFormStars.length > 0) {
        activeFormStars.forEach(s => {
          s.classList.remove('text-yellow-400');
          s.classList.add('text-gray-400');
        });
      }

      const inputField = document.getElementById('newCommentInput');
      if (inputField) inputField.value = '';

      // Update Comment Form URL
      const form = document.getElementById('commentForm');
      if (form) form.action = `/add_comment/${data.id}`;

      // Fetch Comments
      if (commentsList) {
        commentsList.innerHTML =
          '<p class="text-gray-500 italic text-center py-4">Loading reviews...</p>';

        fetch(`/api/comments/${data.id}`)
          .then(response => response.json())
          .then(result => {
            if (result.status === 'success') {
              const comments = result.comments;

              if (comments.length === 0) {
                commentsList.innerHTML =
                  '<p class="text-gray-500 italic text-center py-4">No reviews yet. Be the first!</p>';
                return;
              }

              let html = '';
              comments.forEach(c => {
                let starsVisual = '';
                if (c.rating > 0) {
                  starsVisual = `<span class="text-yellow-400 text-xs ml-2">`;
                  for (let i = 0; i < c.rating; i++) starsVisual += '★';
                  starsVisual += `</span>`;
                }

                let deleteBtn = '';
                if (c.can_delete) {
                  deleteBtn = `
                    <form method="POST" action="/delete_comment/${c.id}" class="absolute top-2 right-2">
                        <button type="submit" class="text-gray-500 hover:text-red-500 transition-colors cursor-pointer" title="Delete Review">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                        </button>
                    </form>`;
                }

                html += `
                  <div class="bg-gray-900 p-3 rounded-card border border-gray-700 relative js-comment-box" data-comment-id="${c.id}">
                      <span class="font-bold text-accent text-xs">${c.author}</span>
                      <span class="text-gray-500 text-xs ml-2">${c.date}</span>
                      ${starsVisual}
                      ${deleteBtn}
                      <p class="mt-1">${c.text}</p>
                  </div>`;
              });

              commentsList.innerHTML = html;
            }
          })
          .catch(error => {
            console.error('Error fetching comments:', error);
            commentsList.innerHTML =
              '<p class="text-red-500 italic py-4">Error loading reviews.</p>';
          });
      }

      // Show the modal
      modal.classList.remove('hidden');
      modal.classList.add('flex');

      const sidebar = document.getElementById('filterSidebar');
      if (sidebar) sidebar.style.opacity = '0';
    }
  });
});

// Global Close Function
window.closeModal = function () {
  const modal = document.getElementById('itemModal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');

    const sidebar = document.getElementById('filterSidebar');
    if (sidebar) sidebar.style.opacity = '1';
  }

};

// Close modal on Escape key press
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    window.closeModal();
  }
});
