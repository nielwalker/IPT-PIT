function renderSections() {
    const container = document.querySelector('.form-container');
    container.innerHTML = '<h5>Sections & Interns</h5><div id="sections-list">Loading...</div>';
    fetch('/coordinator/sections/')
        .then(response => response.json())
        .then(data => {
            const listDiv = document.getElementById('sections-list');
            if (data.sections && Object.keys(data.sections).length > 0) {
                let html = '';
                for (const [section, interns] of Object.entries(data.sections)) {
                    html += `<div style="margin-bottom:1.5rem;">
                        <strong>${section}</strong>
                        <ul style="margin-left:1rem;">` +
                        interns.map(i => `<li>${i.first_name} ${i.last_name} (${i.username})</li>`).join('') +
                        `</ul>
                    </div>`;
                }
                listDiv.innerHTML = html;
            } else {
                listDiv.innerHTML = '<p>No sections or interns found.</p>';
            }
        });
}

// Attach to Manage Sections button
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-button').forEach(btn => {
        btn.addEventListener('click', function() {
            if (this.textContent.trim() === 'Manage Sections') {
                renderSections();
            }
        });
    });
});