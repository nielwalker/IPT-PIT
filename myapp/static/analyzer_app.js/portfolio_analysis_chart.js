function createSkillsChart(skillsData) {
  const ctx = document.getElementById('skillsChart').getContext('2d');
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels: skillsData.labels, // ['a', 'b', ..., 'o']
      datasets: [{
        label: 'PO Frequency in Learnings',
        data: skillsData.values, // corresponding frequencies
        backgroundColor: 'rgba(0, 238, 12, 0.6)',
        borderColor: 'rgb(0, 99, 165)',
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          precision: 0
        }
      },
      responsive: true,
      plugins: {
        legend: { display: false },
        title: {
          display: true,
          text: 'PO Frequency Analysis',
          font: { size: 16 }
        }
      }
    }
  });
}

document.addEventListener('DOMContentLoaded', function () {
  fetch("/static/json/po_graph_data.json")
    .then(response => response.json())
    .then(data => {
      const ctx = document.getElementById('skillsChart').getContext('2d');
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: data.labels,
          datasets: [{
            label: 'PO Frequency in Learnings',
            data: data.data,
            backgroundColor: 'rgba(0, 238, 12, 0.6)',
            borderColor: 'rgb(0, 99, 165)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Percentage'
              }
            },
            x: {
              title: {
                display: true,
                text: 'PO Code'
              }
            }
          },
          plugins: {
            legend: { display: false },
            title: {
              display: true,
              text: 'PO Frequency Analysis',
              font: { size: 16 }
            }
          }
        }
      });
    })
    .catch(err => console.error("Failed to load PO chart data:", err));
});
