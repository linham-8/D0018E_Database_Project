function setWear(min, max) {
  document.getElementById('min_float').value = min;
  document.getElementById('max_float').value = max;
}

document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('itemModal');
  if (!modal) return;

  document.body.addEventListener('click', e => {
    const card = e.target.closest('.js-skin-card');

    if (card) {
      const data = card.dataset;

      document.getElementById('modalItemId').textContent =
        'Item id #' + data.id;
      document.getElementById('modalName').textContent = data.name;
      document.getElementById('modalPrice').textContent = data.price + '€';
      document.getElementById('modalWear').textContent = data.wear;
      document.getElementById('modalRarity').textContent = data.rarity;

      const imgElement = document.getElementById('modalImage');
      imgElement.src = data.image;
      imgElement.alt = data.name;

      // 4. Populate Advanced Stats
      document.getElementById('modalFloat').textContent = data.float;
      document.getElementById('modalSeed').textContent = data.seed;

      // 5. Handle Pattern UI
      const patternContainer = document.getElementById('modalPatternContainer');
      if (data.pattern && data.pattern !== 'None' && data.pattern !== '') {
        document.getElementById('modalPattern').textContent = data.pattern;
        patternContainer.classList.remove('hidden');
        patternContainer.classList.add('flex');
      } else {
        patternContainer.classList.add('hidden');
        patternContainer.classList.remove('flex');
      }

      // 6. Handle StatTrak UI
      const statTrakBadge = document.getElementById('modalStatTrak');
      if (data.stattrak === 'True' || data.stattrak === 'true') {
        statTrakBadge.classList.remove('hidden');
        statTrakBadge.classList.add('block');
      } else {
        statTrakBadge.classList.add('hidden');
        statTrakBadge.classList.remove('block');
      }

      // Optional: Store ID globally for the future Add to Cart button
      window.currentSelectedItemId = data.id;

      // 7. Show the modal
      modal.classList.remove('hidden');
      modal.classList.add('flex');
    }
  });
});

// Global Close Function
window.closeModal = function () {
  const modal = document.getElementById('itemModal');
  if (modal) {
    modal.classList.add('hidden');
    modal.classList.remove('flex');
  }
};

// Close modal on Escape key press
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    window.closeModal();
  }
});
