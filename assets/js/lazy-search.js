(function() {
  'use strict';
  
  if (typeof lunr === 'undefined') {
    let searchLoaded = false;
    
    function loadSearch() {
      if (searchLoaded) return;
      searchLoaded = true;
      
      const scripts = [
        '/assets/js/lunr/lunr.min.js',
        '/assets/js/lunr/lunr-store.js', 
        '/assets/js/lunr/lunr-en.js'
      ];
      
      function loadScript(src) {
        return new Promise(function(resolve, reject) {
          const script = document.createElement('script');
          script.src = src;
          script.onload = resolve;
          script.onerror = reject;
          document.body.appendChild(script);
        });
      }
      
      // Load scripts sequentially
      scripts.reduce(function(promise, src) {
        return promise.then(function() {
          return loadScript(src);
        });
      }, Promise.resolve());
    }
    
    // Attach listeners when DOM is ready
    function attachListeners() {
      const searchBtn = document.querySelector('.search__toggle');
      const searchInput = document.querySelector('input[type="text"].search');
      
      if (searchBtn) {
        searchBtn.addEventListener('mouseenter', loadSearch, { once: true });
        searchBtn.addEventListener('click', loadSearch, { once: true });
      }
      
      if (searchInput) {
        searchInput.addEventListener('focus', loadSearch, { once: true });
      }
    }
    
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', attachListeners);
    } else {
      attachListeners();
    }
  }
})();