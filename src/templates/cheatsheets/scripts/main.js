      // Key label mappings
      const keyLabelMappings = {
        Darwin: {
          Cmd: "⌘",
          Alt: "⌥",
          Ctrl: "⌃",
          Shift: "Shift",
          CapsLock: "Caps",
          Tab: "Tab",
          Enter: "↩",
          Backspace: "⌫",
          Space: "",
          Esc: "Esc",
          "Left": "←",
          "Down": "↓",
          "Up": "↑",
          "Right": "→",
        },
        Windows: {
          Cmd: "Win",
          Alt: "Alt",
          Ctrl: "Ctrl",
          Shift: "Shift",
          CapsLock: "Caps",
          Tab: "Tab",
          Enter: "Enter",
          Backspace: "Backspace",
          Space: "Space",
          Esc: "Esc",
          "←": "←",
          "↓": "↓",
          "↑": "↑",
          "→": "→",
        },
        Linux: {
          Cmd: "Super",
          Alt: "Alt",
          Ctrl: "Ctrl",
          Shift: "Shift",
          CapsLock: "Caps",
          Tab: "Tab",
          Enter: "Enter",
          Backspace: "Backspace",
          Space: "Space",
          Esc: "Esc",
          "←": "←",
          "↓": "↓",
          "↑": "↑",
          "→": "→",
        },
      };

      function getKeyLabel(key, system) {
        return keyLabelMappings[system][key] || key;
      }

    function wrapModifierSymbols(text) {
        // Define the symbols we want to make larger
        const modifierSymbols = ['⌘', '⌥', '⌃', '⇧'];

        // Replace each modifier symbol with a wrapped version
        modifierSymbols.forEach(symbol => {
            text = text.replace(
                new RegExp(symbol, 'g'),
                `<span class="modifier-symbol">${symbol}</span>`
            );
        });

        return text;
    }
      function generateKeyboard() {
        const keyboard = document.getElementById("keyboard");
        const layout = keyboard.getAttribute("data-layout");
        const system = keyboard.getAttribute("data-system");
        const keyboardLayout = {{ keyboard_layout | tojson | safe }};

        keyboard.innerHTML = "";

        keyboardLayout.forEach((row) => {
          const rowDiv = document.createElement("div");
          rowDiv.className = "row";

          row.forEach((key) => {
            if (key === "↑↓") {
              const stackDiv = document.createElement("div");
              stackDiv.className = "key-stack";

              const upKeyDiv = document.createElement("div");
              upKeyDiv.className = "key key__arrow key__arrow-half";
              upKeyDiv.setAttribute("data-key", "↑");
              upKeyDiv.textContent = getKeyLabel("↑", system);

              const downKeyDiv = document.createElement("div");
              downKeyDiv.className = "key key__arrow key__arrow-half";
              downKeyDiv.setAttribute("data-key", "↓");
              downKeyDiv.textContent = getKeyLabel("↓", system);

              stackDiv.appendChild(upKeyDiv);
              stackDiv.appendChild(downKeyDiv);
              rowDiv.appendChild(stackDiv);
            } else {
              const keyDiv = document.createElement("div");
              keyDiv.className = "key";
              keyDiv.setAttribute("data-key", key);
              keyDiv.textContent = getKeyLabel(key, system);

              // Add specific classes for special keys
              if (["Backspace", "Tab", "CapsLock", "Enter", "Shift"].includes(key)) {
                keyDiv.classList.add(`key__${key.toLowerCase()}`);
              } else if (key === "Space") {
                keyDiv.classList.add("key__spacebar");
              } else if (["←", "→"].includes(key)) {
                keyDiv.classList.add("key__arrow");
              }

              rowDiv.appendChild(keyDiv);
            }
          });

          keyboard.appendChild(rowDiv);
        });
      }

      // Call generateKeyboard on page load
      document.addEventListener("DOMContentLoaded", generateKeyboard);

      // Dark-Mode toggle functionality
      const darkModeToggle = document.getElementById('dark-mode-toggle');
      const themeIcon = document.getElementById("theme-icon");
      const body = document.body;

      function updateDarkModeToggle() {
        themeIcon.textContent = body.classList.contains("dark-mode")
          ? "☀️"
          : "🌙";
      }

      darkModeToggle.addEventListener("click", () => {
        body.classList.toggle("dark-mode");
        localStorage.setItem("darkMode", body.classList.contains("dark-mode"));
        updateDarkModeToggle();
        adjustLayout();
      });

      function scrollToSection(targetId) {
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
          const headerOffset = 60; // Adjust this value based on your header height
          const elementPosition = targetElement.getBoundingClientRect().top;
          const offsetPosition =
            elementPosition + window.pageYOffset - headerOffset;

          window.scrollTo({
            top: offsetPosition,
            behavior: "smooth",
          });
        }
      }

      // Check for saved dark mode preference, default to dark mode
      if (localStorage.getItem("darkMode") === null) {
        localStorage.setItem("darkMode", "true");
      }

      if (localStorage.getItem("darkMode") === "true") {
        body.classList.add("dark-mode");
      } else {
        body.classList.remove("dark-mode");
      }

      updateDarkModeToggle();
      adjustLayout();

      function highlightKeys(shortcut) {
        // Clear any previously highlighted keys
        document.querySelectorAll(".key").forEach((key) => key.classList.remove("active"));

        // Get the shortcut key parts
        const shortcutParts = shortcut.split('+').map(part => part.trim());
        const system = document.getElementById("keyboard").getAttribute("data-system");

        shortcutParts.forEach((keyToFind) => {
            keyToFind = keyToFind.toLowerCase();
            const keyElements = document.querySelectorAll(".key");

            keyElements.forEach((element) => {
                const dataKey = element.getAttribute("data-key").toLowerCase();
                const keyLabel = element.textContent.toLowerCase();

                if (
                    dataKey === keyToFind ||
                    keyLabel === keyToFind ||
                    (keyToFind === "cmd" && (dataKey === "cmd" || dataKey === "win" || dataKey === "super"))
                ) {
                    element.classList.add("active");
                }
            });
        });
      }

      document.querySelectorAll(".shortcut").forEach((shortcut) => {
        {% if not allow_text %}
        shortcut.addEventListener("click", function() {
            // Get the text content and replace <sep> with +
            const shortcutKey = this.querySelector(".shortcut-key").textContent.replace(/\s*\+\s*/g, '+');
            highlightKeys(shortcutKey);
        });
        {% endif %}
      });

      // Keep original case for key data-attributes
      document.querySelectorAll(".key").forEach((key) => {
        const dataKey = key.getAttribute("data-key");
        key.setAttribute("data-key", dataKey);
      });

      // Category navigation
      const categoryNavToggle = document.getElementById("category-nav-toggle");
      const categoryNav = document.getElementById("category-nav");

      function toggleCategoryNav() {
        categoryNavToggle.classList.toggle("active");
        categoryNav.classList.toggle("active");
        document.body.classList.toggle("nav-active");
        adjustLayout();
        adjustSearchContainer();
      }

      function adjustLayout() {
        const isNavActive = document.body.classList.contains("nav-active");
        const shortcutKeys = document.querySelectorAll(".shortcut-key");
        const shortcutDescriptions = document.querySelectorAll(".shortcut-description");
        const shortcuts = document.querySelectorAll(".shortcut");

        shortcuts.forEach((shortcut) => {
          shortcut.style.flexDirection = "row";
          shortcut.style.alignItems = "flex-start";
          shortcut.style.minHeight = "40px";
          shortcut.style.height = "auto";
          shortcut.style.padding = "8px";
        });

        shortcutKeys.forEach((key) => {
          key.style.fontSize = isNavActive ? "0.85rem" : "0.95rem";
          key.style.marginRight = "8px";
          key.style.marginBottom = "0";
          key.style.width = isNavActive ? "40%" : "50%";
          key.style.wordWrap = "break-word";
          key.style.overflowWrap = "break-word";
        });

        shortcutDescriptions.forEach((desc) => {
          desc.style.fontSize = isNavActive ? "0.75rem" : "0.85rem";
          desc.style.textAlign = "right";
          desc.style.width = isNavActive ? "60%" : "50%";
          desc.style.wordWrap = "break-word";
          desc.style.overflowWrap = "break-word";
        });
      }

      function adjustSearchContainer() {
        const searchContainer = document.querySelector(".search-container");
        const isNavActive = document.body.classList.contains("nav-active");
        searchContainer.style.marginLeft = isNavActive ? "220px" : "20px";
        document.getElementById("shortcut-search").style.width = isNavActive
          ? "calc(100% - 200px)"
          : "100%";
      }

      categoryNavToggle.addEventListener("click", (e) => {
        e.stopPropagation();
        toggleCategoryNav();
      });

      document.querySelectorAll("#category-nav a").forEach((link) => {
        link.addEventListener("click", (e) => {
          e.preventDefault();
          const targetId = link.getAttribute("href").slice(1);
          scrollToSection(targetId);
          toggleCategoryNav();
        });
      });

      // Close category nav when clicking outside
      document.addEventListener("click", (e) => {
        if (
          !categoryNav.contains(e.target) &&
          e.target !== categoryNavToggle &&
          categoryNav.classList.contains("active")
        ) {
          toggleCategoryNav();
        }
      });

      // Prevent clicks inside the nav from closing it
      categoryNav.addEventListener("click", (e) => {
        e.stopPropagation();
      });

      // Initial category navigation update
      updateCategoryNavigation();

      // Search functionality
      const searchInput = document.getElementById("shortcut-search");
      const shortcuts = document.querySelectorAll(".shortcut");

      searchInput.addEventListener("input", function () {
        const searchTerm = this.value.toLowerCase();
        const sections = document.querySelectorAll(".section");

        sections.forEach((section) => {
          const shortcuts = section.querySelectorAll(".shortcut");
          let hasVisibleShortcuts = false;

          shortcuts.forEach((shortcut) => {
            const description = shortcut
              .querySelector(".shortcut-description")
              .textContent.toLowerCase();
            const key = shortcut
              .querySelector(".shortcut-key")
              .textContent.toLowerCase();
            if (description.includes(searchTerm) || key.includes(searchTerm)) {
              shortcut.style.display = "";
              hasVisibleShortcuts = true;
            } else {
              shortcut.style.display = "none";
            }
          });

          section.style.display = hasVisibleShortcuts ? "" : "none";
        });

        // Update category navigation
        updateCategoryNavigation();
      });

      function updateCategoryNavigation() {
        const categoryLinks = document.querySelectorAll("#category-nav a");
        categoryLinks.forEach((link) => {
          const targetId = link.getAttribute("href").slice(1);
          const targetSection = document.getElementById(targetId);
          if (targetSection) {
            link.style.display = targetSection.style.display;
          }
        });
      }
