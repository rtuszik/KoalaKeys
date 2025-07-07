const cheatsheetList = document.getElementById('cheatsheet-list');
const searchInput = document.getElementById('search');
const sortSelect = document.getElementById('sort');
const itemsPerPageSelect = document.getElementById('items-per-page');
const noResults = document.getElementById('no-results');
const darkModeToggle = document.getElementById('dark-mode-toggle');
const prevPageButton = document.getElementById('prev-page');
const nextPageButton = document.getElementById('next-page');
const body = document.body;

const themeIcon = document.getElementById("theme-icon");

function updateDarkModeToggle() {
themeIcon.textContent = body.classList.contains("dark-mode")
    ? "☀️"
    : "🌙";
}

darkModeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', body.classList.contains('dark-mode'));
    updateDarkModeToggle();
});

// Check for saved dark mode preference, default to dark mode
if (localStorage.getItem('darkMode') === null) {
    localStorage.setItem('darkMode', 'true');
}

if (localStorage.getItem('darkMode') === 'true') {
    body.classList.add('dark-mode');
} else {
    body.classList.remove('dark-mode');
}

updateDarkModeToggle();

const cheatsheets = [
    {% for cheatsheet in cheatsheets %}
    { title: "{{ cheatsheet.title }}", filename: "{{ cheatsheet.filename }}" },
    {% endfor %}
];

let currentPage = 1;
let itemsPerPage = 9;

function updateCheatsheets() {
    const searchTerm = searchInput.value.toLowerCase();
    const sortOrder = sortSelect.value;

    let filteredCheatsheets = cheatsheets.filter(cheatsheet =>
        cheatsheet.title.toLowerCase().includes(searchTerm)
    );

    filteredCheatsheets.sort((a, b) => {
        if (sortOrder === 'name-asc') {
            return a.title.localeCompare(b.title);
        } else {
            return b.title.localeCompare(a.title);
        }
    });

    const totalPages = Math.ceil(filteredCheatsheets.length / itemsPerPage);
    currentPage = Math.min(currentPage, totalPages);

    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageCheatsheets = filteredCheatsheets.slice(startIndex, endIndex);

    cheatsheetList.innerHTML = pageCheatsheets.map(cheatsheet => `
        <li class="cheatsheet-item">
            <a href="${cheatsheet.filename}" class="cheatsheet-link">
                <div class="cheatsheet-title">${cheatsheet.title}</div>
            </a>
        </li>
    `).join('');

    noResults.style.display = filteredCheatsheets.length === 0 ? 'block' : 'none';

    prevPageButton.disabled = currentPage === 1;
    nextPageButton.disabled = currentPage === totalPages;

    updateLayout();
}

function updateLayout() {
    const containerWidth = cheatsheetList.offsetWidth;
    const itemWidth = 250; // Approximate width of each item
    const columns = Math.floor(containerWidth / itemWidth);
    cheatsheetList.style.gridTemplateColumns = `repeat(${columns}, 1fr)`;
}

searchInput.addEventListener('input', () => {
    currentPage = 1;
    updateCheatsheets();
});
sortSelect.addEventListener('change', updateCheatsheets);
itemsPerPageSelect.addEventListener('change', (e) => {
    itemsPerPage = parseInt(e.target.value);
    currentPage = 1;
    updateCheatsheets();
});

prevPageButton.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        updateCheatsheets();
    }
});

nextPageButton.addEventListener('click', () => {
    currentPage++;
    updateCheatsheets();
});

window.addEventListener('resize', updateLayout);

updateCheatsheets();

