// Modal Data Storage
const modalData = {
    brand: [],
    model: [],
    town: []
};

let currentModalField = null;
let allModalItems = [];

// Open Modal
function openModal(field, title) {
    currentModalField = field;
    document.getElementById('modalTitle').textContent = title;
    document.getElementById('modalSearch').value = '';
    document.getElementById('modalOverlay').classList.add('show');
    
    // Populate modal items
    populateModalItems(modalData[field] || []);
    
    // Focus search input
    setTimeout(() => {
        document.getElementById('modalSearch').focus();
    }, 100);
}

// Close Modal
function closeModal(event) {
    if (event) {
        event.stopPropagation();
    }
    document.getElementById('modalOverlay').classList.remove('show');
    currentModalField = null;
}

// Populate Modal Items
function populateModalItems(items) {
    allModalItems = items;
    const modalBody = document.getElementById('modalBody');
    
    if (items.length === 0) {
        modalBody.innerHTML = '<div class="modal-item" style="color: #999; cursor: default;">No items available</div>';
        return;
    }
    
    modalBody.innerHTML = items.map(item => 
        `<div class="modal-item" onclick="selectModalItem('${item}')">${item}</div>`
    ).join('');
}

// Filter Modal Items
function filterModalItems() {
    const searchValue = document.getElementById('modalSearch').value.toLowerCase();
    const filteredItems = allModalItems.filter(item => 
        item.toLowerCase().includes(searchValue)
    );
    
    const modalBody = document.getElementById('modalBody');
    
    if (filteredItems.length === 0) {
        modalBody.innerHTML = '<div class="modal-item" style="color: #999; cursor: default;">No matching items</div>';
        return;
    }
    
    modalBody.innerHTML = filteredItems.map(item => 
        `<div class="modal-item" onclick="selectModalItem('${item}')">${item}</div>`
    ).join('');
}

// Select Modal Item
function selectModalItem(value) {
    if (currentModalField) {
        document.getElementById(currentModalField).value = value;
    }
    closeModal();
}

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Form Submission
document.getElementById('priceForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const btn = document.getElementById('priceBtn');
    const btnText = btn.querySelector('.btn-text');
    const loading = btn.querySelector('.loading');
    const priceDisplay = document.getElementById('priceDisplay');
    
    // Collect form data
    const formData = {
        brand: document.getElementById('brand').value,
        model: document.getElementById('model').value,
        yom: parseInt(document.getElementById('yom').value) || null,
        engineCC: parseInt(document.getElementById('engineCC').value) || null,
        gear: document.getElementById('gear').value,
        fuelType: document.getElementById('fuelType').value,
        mileage: parseInt(document.getElementById('mileage').value) || null,
        town: document.getElementById('town').value,
        date: document.getElementById('date').value,
        condition: document.getElementById('condition').value,
        leasing: document.getElementById('leasing').checked,
        airCondition: document.getElementById('airCondition').checked,
        powerSteering: document.getElementById('powerSteering').checked,
        powerMirror: document.getElementById('powerMirror').checked,
        powerWindow: document.getElementById('powerWindow').checked
    };
    
    // Show loading state
    btnText.style.display = 'none';
    loading.classList.add('show');
    btn.disabled = true;
    
    try {
        // Convert form data to query parameters for GET request
        const queryParams = new URLSearchParams();
        for (const [key, value] of Object.entries(formData)) {
            if (value !== null && value !== '') {
                queryParams.append(key, value);
            }
        }
        
        // Send GET request
        const response = await fetch(`http://localhost/price?${queryParams.toString()}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        
        const data = await response.json();
        
        // Display price
        const price = data.price || data.predicted_price || 0;
        document.getElementById('priceValue').textContent = `Rs. ${formatPrice(price)}`;
        priceDisplay.classList.add('show');
        
    } catch (error) {
        console.error('Error:', error);
        // For demo purposes, show a sample price
        document.getElementById('priceValue').textContent = `Rs. --`;
        priceDisplay.classList.add('show');
    } finally {
        // Reset button state
        btnText.style.display = 'inline';
        loading.classList.remove('show');
        btn.disabled = false;
    }
});

// Format price with commas
function formatPrice(price) {
    return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// Set default date to today
document.addEventListener('DOMContentLoaded', function() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('date').value = today;
});
