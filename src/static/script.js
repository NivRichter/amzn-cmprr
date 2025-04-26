async function search() {
    const query = document.getElementById('searchQuery').value.trim();
    const searchType = document.querySelector('input[name="searchType"]:checked').value;
    
    if (!query) {
        alert('Please enter a search query');
        return;
    }

    // Show loading state
    document.getElementById('loading').style.display = 'block';
    document.getElementById('results').innerHTML = '';

    try {
        const response = await fetch('http://localhost:8000/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: searchType,
                query: query
            })
        });

        const data = await response.json();

        if (response.ok) {
            displayResults(data);
        } else {
            displayError(data.error || 'An error occurred');
        }
    } catch (error) {
        displayError('Failed to connect to the server');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

function displayResults(results) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    if (Object.keys(results).length === 0) {
        resultsDiv.innerHTML = '<div class="error">No results found</div>';
        return;
    }

    const resultsList = document.createElement('div');
    resultsList.className = 'results-list';

    for (const [country, data] of Object.entries(results)) {
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item';
        
        if (data) {
            resultItem.innerHTML = `
                <div class="result-header">
                    <span class="country">${country}</span>
                    <span class="price">${data.price} ${data.currency}</span>
                </div>
                <div class="result-details">
                    <div class="preview-container">
                        <a href="${data.url}" target="_blank" class="preview-link" 
                           data-country="${country}"
                           data-url="${data.url}"
                           onmouseover="showPreview(this)"
                           onmouseout="hidePreview(this)">View Product</a>
                        <div class="preview-tooltip" id="preview-${country}">
                            <div class="preview-content">
                                <div class="preview-image">
                                    <img src="${data.image_url || '/static/placeholder.png'}" alt="Product Preview">
                                </div>
                                <div class="preview-info">
                                    <h3>${data.title || 'Product Preview'}</h3>
                                    <p class="preview-price">${data.price} ${data.currency}</p>
                                    <p class="preview-country">${country}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="url">${data.url}</div>
                </div>
            `;
        } else {
            resultItem.innerHTML = `
                <div class="result-header">
                    <span class="country">${country}</span>
                    <span class="price">Not available</span>
                </div>
            `;
        }
        
        resultsList.appendChild(resultItem);
    }

    resultsDiv.appendChild(resultsList);
}

function showPreview(element) {
    const country = element.getAttribute('data-country');
    const tooltip = document.getElementById(`preview-${country}`);
    if (tooltip) {
        tooltip.style.display = 'block';
    }
}

function hidePreview(element) {
    const country = element.getAttribute('data-country');
    const tooltip = document.getElementById(`preview-${country}`);
    if (tooltip) {
        tooltip.style.display = 'none';
    }
}

function displayError(message) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `<div class="error">${message}</div>`;
} 