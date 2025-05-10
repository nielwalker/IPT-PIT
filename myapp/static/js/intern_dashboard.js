document.addEventListener('DOMContentLoaded', () => {
    const weekTabsContainer = document.querySelector('.week-tabs');
    const formContainer = document.querySelector('.form-container');
    const navButtons = document.querySelectorAll('.nav-button');

    const weekData = [
        { id: 'week1', label: 'Week 1' },
        { id: 'week2', label: 'Week 2' },
        { id: 'week3', label: 'Week 3' },
        { id: 'week4', label: 'Week 4' },
        { id: 'week5', label: 'Week 5' },
        { id: 'week6', label: 'Week 6' },
        { id: 'week7', label: 'Week 7' },
        { id: 'week8', label: 'Week 8' },
        { id: 'week9', label: 'Week 9' },
        { id: 'week10', label: 'Week 10' },
        { id: 'week11', label: 'Week 11' },
        { id: 'week12', label: 'Week 12' },
    ];

    function createWeekDropdown() {
        const weekSelect = document.getElementById('week-select');
        if (!weekSelect) {
            console.error('week-select element not found!');
            return;
        }

        weekSelect.innerHTML = ''; // Clear existing options

        // Populate the dropdown with weekData
        weekData.forEach(week => {
            const option = document.createElement('option');
            option.value = week.id; // This must match the database value
            option.textContent = week.label;
            weekSelect.appendChild(option);
        });

        // Add event listener to handle dropdown changes
        weekSelect.addEventListener('change', (event) => {
            const selectedWeekId = event.target.value;
            showWeekReport(selectedWeekId);
        });

        // Show the first week's report by default
        if (weekData.length > 0) {
            weekSelect.value = weekData[0].id;
            showWeekReport(weekData[0].id);
        }
    }

    function showWeekReport(weekId) {
        const form = document.getElementById('week-form');
        if (!form) {
            console.error('Form element not found!');
            return;
        }

        const table = document.createElement('table');
        table.id = 'report-form';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Date</th>
                    <th>No. of Hours</th>
                    <th>Activities/Tasks</th>
                    <th>Score</th>
                    <th>New Learnings</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><input type="date" name="date"></td>
                    <td><input type="number" name="hours" min="0"></td>
                    <td><textarea name="activities"></textarea></td>
                    <td><input type="text" name="score"></td>
                    <td><textarea name="learnings"></textarea></td>
                </tr>
            </tbody>
        `;

        // Clear existing table and append the new one
        form.innerHTML = '';
        form.appendChild(table);

        const submitButton = document.createElement('button');
        submitButton.id = 'submit-button';
        submitButton.type = 'submit';
        submitButton.textContent = 'Submit';
        form.appendChild(submitButton);

        // Attach the submit event handler here!
        form.onsubmit = function(event) {
            event.preventDefault();

            const formData = new FormData(form);
            formData.append('week', weekId);

            fetch('/add-week-report/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                }
            })
            .then(response => {
                if (response.ok) {
                    alert('Week report submitted successfully!');
                    form.reset();
                } else {
                    alert('Failed to submit the week report.');
                }
            })
            .catch(error => console.error('Error:', error));
        };
    }

    function handleNavClick(action) {
        formContainer.innerHTML = ''; // Clear form container

        if (action === 'add-week-report') {
            formContainer.innerHTML = `
                <div class="week-dropdown">
                    <label for="week-select" class="week-label">Select Week:</label>
                    <select id="week-select" class="week-select">
                        <!-- Options will be dynamically added here -->
                    </select>
                </div>
                <form id="week-form">
                    <!-- Table will be dynamically added here -->
                </form>
            `;
            createWeekDropdown(); // Create the dropdown for weeks
        } else if (action === 'upload-journal') {
            formContainer.innerHTML = `
                <h3>Upload Journal Section</h3>
                <p>Please upload your journal in PDF format:</p>
                <form id="upload-journal-form">
                    <input type="file" id="journal-file" name="journal-file" accept="application/pdf" />
                    <button type="submit" id="upload-button">Upload</button>
                </form>
            `;
        } else if (action === 'overview') {
            renderOverviewSection();
        }
    }

    function renderOverviewSection() {
        const container = document.querySelector('.form-container');
        container.innerHTML = `
            <div id="overview-container">
                <label for="overview-week-select" class="week-label">Select Week:</label>
                <select id="overview-week-select" class="week-select"></select>
                <div id="overview-table-container" style="margin-top:1rem;"></div>
            </div>
        `;

        fetch('/get-week-reports/')
            .then(response => response.json())
            .then(data => {
                const weekSelect = document.getElementById('overview-week-select');
                const tableContainer = document.getElementById('overview-table-container');
                // Populate dropdown
                weekSelect.innerHTML = data.weeks.map(week => `<option value="${week}">${week}</option>`).join('');
                // Render table for selected week
                function renderTable(week) {
                    let reports = data.reports[week] || [];
                    // Sort reports by date (ascending)
                    reports = reports.slice().sort((a, b) => new Date(a.date) - new Date(b.date));
                    if (reports.length === 0) {
                        tableContainer.innerHTML = '<p>No reports for this week.</p>';
                        return;
                    }
                    let rows = reports.map(r => `
                        <tr>
                            <td>${r.date}</td>
                            <td>${r.hours}</td>
                            <td>${r.activities}</td>
                            <td>${r.score}</td>
                            <td>${r.new_learnings}</td>
                        </tr>
                    `).join('');
                    tableContainer.innerHTML = `
                        <table class="table table-bordered overview-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>No. of Hours</th>
                                    <th>Activities/Tasks</th>
                                    <th>Score</th>
                                    <th>New Learnings</th>
                                </tr>
                            </thead>
                            <tbody>${rows}</tbody>
                        </table>
                    `;
                }
                // Initial render
                if (data.weeks.length > 0) renderTable(data.weeks[0]);
                weekSelect.addEventListener('change', () => renderTable(weekSelect.value));
            });
    }

    // Event Listeners for Navigation Buttons
    navButtons.forEach(button => {
        button.addEventListener('click', () => {
            const action = button.dataset.action;
            handleNavClick(action);
        });
    });

    // Initialize - Show "Add Week Report" section on initial load
    handleNavClick('add-week-report');
});

document.getElementById('week-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission

    const formData = new FormData(this);
    const selectedWeek = document.getElementById('week-select').value; // Get the selected week
    formData.append('week', selectedWeek); // Add the selected week to the form data

    fetch('/add-week-report/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (response.ok) {
            alert('Week report submitted successfully!');
            this.reset(); // Reset the form
        } else {
            alert('Failed to submit the week report.');
        }
    })
    .catch(error => console.error('Error:', error));
});