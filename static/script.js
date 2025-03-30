document.getElementById('file').addEventListener('change', function () {
    const fileNameDisplay = document.getElementById('file-name');
    
    if (this.files.length > 0) {
      fileNameDisplay.textContent = `📁 Selected File: ${this.files[0].name}`;
      fileNameDisplay.classList.remove('hidden');
    } else {
      fileNameDisplay.textContent = 'No file chosen';
      fileNameDisplay.classList.add('hidden');
    }
  });
  
  document.getElementById('upload-form').addEventListener('submit', async function (e) {
    e.preventDefault();
    
    const loader = document.getElementById('loader');
    const result = document.getElementById('result');
  
    loader.classList.remove('hidden');
    result.classList.add('hidden');
  
    const formData = new FormData();
    formData.append('file', document.getElementById('file').files[0]);
  
    try {
      const response = await fetch('/upload', {
        method: 'POST',
        body: formData,
      });
  
      if (response.ok) {
        const data = await response.json();
        displayEntities(data);
      } else {
        alert('Failed to extract entities. Please try again.');
      }
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      loader.classList.add('hidden');
    }
  });
  
  function displayEntities(entities) {
    const tableBody = document.querySelector('#entityTable tbody');
    const filterSelect = document.getElementById('entityFilter');
    const totalEntitiesDisplay = document.getElementById('totalEntities');
    const entitySummaryDisplay = document.getElementById('entitySummary');
  
    tableBody.innerHTML = '';
    filterSelect.innerHTML = '<option value="All">All</option>';
    
    const labels = new Map();
    entities.forEach(entity => {
      const row = `<tr><td>${entity[0]}</td><td>${entity[1]}</td></tr>`;
      tableBody.innerHTML += row;
  
      labels.set(entity[1], (labels.get(entity[1]) || 0) + 1);
    });
  
    totalEntitiesDisplay.textContent = entities.length;
    entitySummaryDisplay.textContent = Array.from(labels)
      .map(([label, count]) => `${label}: ${count}`)
      .join(', ');
  
    labels.forEach((_, label) => {
      filterSelect.innerHTML += `<option value="${label}">${label}</option>`;
    });
  
    document.getElementById('result').classList.remove('hidden');
  }
  
  // Filtering
  document.getElementById('entityFilter').addEventListener('change', function () {
    const selectedLabel = this.value;
    const rows = document.querySelectorAll('#entityTable tbody tr');
  
    rows.forEach(row => {
      const label = row.children[1].textContent;
      row.style.display = (selectedLabel === 'All' || label === selectedLabel) ? '' : 'none';
    });
  });
  