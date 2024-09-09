// Constants
const PRECISION = 8;
const initialPoint = [53.0190701, 20.8802902];  // Initial point coordinates - Przasnysz
const COLOR1 = '#0b6d40';
const COLOR2 = '#000000';
const COLOR3 = '#ad192f';

// Default pin icon
const defaultIcon = L.divIcon({
    className: 'custom-icon',
    html: '<svg viewBox="0 0 24 14" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"><path d="M12 2C8.13 2 5 5.13 5 9c0 3.88 7 11 7 11s7-7.12 7-11c0-3.87-3.13-7-7-7zm0 14.5c-1.38 0-2.5-1.12-2.5-2.5S10.62 11.5 12 11.5 14.5 12.62 14.5 14 13.38 16.5 12 16.5z" fill="#ad192f"/></svg>',
    iconSize: [30, 40],  // Adjust size
    iconAnchor: [15, 40], // Anchor the icon at the bottom center
    popupAnchor: [0, -30]
});

// Selected pin icon
const selectedIcon = L.divIcon({
    className: 'custom-icon',
    html: '<svg viewBox="0 0 24 14" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%"><path d="M12 2C8.13 2 5 5.13 5 9c0 3.88 7 11 7 11s7-7.12 7-11c0-3.87-3.13-7-7-7zm0 14.5c-1.38 0-2.5-1.12-2.5-2.5S10.62 11.5 12 11.5 14.5 12.62 14.5 14 13.38 16.5 12 16.5z" fill="#0b6d40"/></svg>',
    iconSize: [30, 40],  // Adjust size
    iconAnchor: [15, 40], // Anchor the icon at the bottom center
    popupAnchor: [0, -30]
});

// Create a map instance
const map = L.map('map', { dragging: true }).setView(initialPoint, 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

let markers = [];
let isAdding = true; // Default mode
let isEditing = false;
let selectedMarkerIndex = null;
let polyline = null; // For connecting the markers with lines

function startAdding() {
    isAdding = true;
    isEditing = false;
    markers.forEach(marker => marker.options.draggable = false);
    markers.forEach(marker => marker.dragging.disable());
    map.dragging.enable(); // Enable map dragging when adding
    
    // Update button styles
    setButtonState('start-adding-button', true);
    setButtonState('start-editing-button', false);
}

function startEditing() {
    isAdding = false;
    isEditing = true;
    markers.forEach(marker => marker.dragging.enable());

    map.dragging.disable(); // Disable map dragging when editing
    
    // Update button styles
    setButtonState('start-adding-button', false);
    setButtonState('start-editing-button', true);
}
function setButtonState(buttonId, isActive) {
    const button = document.getElementById(buttonId);
    if (isActive) {
        button.classList.add('selected');
    } else {
        button.classList.remove('selected');
    }
}

// Add keyboard event listener
document.addEventListener('keydown', function(event) {
    if (event.key.toLowerCase() === 'a') {
        startAdding();
    } else if (event.key.toLowerCase() === 'e') {
        startEditing();
    } else if (event.key === 'Delete') {
        deleteSelectedPoint();  
    }
});

function deleteSelectedPoint() {
    if (selectedMarkerIndex !== null) {
        const marker = markers[selectedMarkerIndex];

        // Determine which marker to select next
        const nextIndex = selectedMarkerIndex + 1 < markers.length ? selectedMarkerIndex + 1 : selectedMarkerIndex - 1;

        // Remove the marker from the map and the array
        map.removeLayer(marker);
        markers.splice(selectedMarkerIndex, 1);

        // Update the marker selection
        if (nextIndex >= 0 && nextIndex < markers.length) {
            selectMarker(nextIndex);
        } else {
            selectedMarkerIndex = null;  // If no markers are left, clear the selection
            clearEditControls();  // Clear input fields
        }

        // Update the map and UI
        updatePointsTable();
        updateMarkerOrderNumbers();
        updatePolyline();
    }
}

// Order markers
function updateMarkerOrderNumbers() {
    // Remove the existing order number labels
    map.eachLayer(layer => {
        if (layer.options && layer.options.icon && layer.options.icon.options && layer.options.icon.options.className === 'order-number-label') {
            map.removeLayer(layer);
        }
    });

    // Update the numbers for each marker on the map
    markers.forEach((marker, index) => {
        const lat = marker.getLatLng().lat;
        const lon = marker.getLatLng().lng;

        L.marker([lat, lon], {
            icon: L.divIcon({
                className: 'order-number-label',
                html: `<div style="font-size:12px; font-weight:bold;">${index + 1}</div>`,
                iconSize: [20, 20]
            })
        }).addTo(map);
    });
}

function clearAllPoints() {
    markers.forEach(marker => map.removeLayer(marker));
    markers = [];
    selectedMarkerIndex = null;

    // Update the map and UI    
    updatePointsTable();
    clearEditControls();
    updatePolyline();
}

function updatePointsTable() {
    const tableBody = document.querySelector('#points-table tbody');
    tableBody.innerHTML = '';
    markers.forEach((marker, index) => {
        const lat = marker.getLatLng().lat.toFixed(PRECISION);
        const lng = marker.getLatLng().lng.toFixed(PRECISION);
        const row = document.createElement('tr');
        row.dataset.index = index;
        row.draggable = true;
        row.innerHTML = `
            <td class="td-index">${index + 1}</td>
            <td>${lat}</td>
            <td>${lng}</td>
            <td class="move-buttons">
                <button onclick="movePoint(${index}, -1); event.stopPropagation();">↑</button>
                <button onclick="movePoint(${index}, 1); event.stopPropagation();">↓</button>
            </td>
        `;
        tableBody.appendChild(row);

        if (index === selectedMarkerIndex) {
            row.classList.add('selected');
        } else {
            row.classList.remove('selected');
        }
    });
}

function selectMarker(index) {
    if (index === null || index >= markers.length) return;

    // Deselect all markers and close all popups
    markers.forEach(marker => {
        marker.setIcon(defaultIcon);
        marker.closePopup();
    });

    // Update selection index
    selectedMarkerIndex = index;
    const marker = markers[selectedMarkerIndex];
    if (marker) {
        marker.setIcon(selectedIcon);
        map.setView(marker.getLatLng());
        marker.openPopup();

        // Update
        updateEditControls(marker);
        updatePointsTable();
    }
}

function movePoint(index, direction) {
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= markers.length) return;

    // Swap markers
    const marker = markers.splice(index, 1)[0];
    markers.splice(newIndex, 0, marker);

    // Update selection index
    if (selectedMarkerIndex === index) {
        selectedMarkerIndex = newIndex;
    } else if (index < selectedMarkerIndex && newIndex >= selectedMarkerIndex) {
        selectedMarkerIndex--;
    } else if (index > selectedMarkerIndex && newIndex <= selectedMarkerIndex) {
        selectedMarkerIndex++;
    }

    selectMarker(selectedMarkerIndex);

    // Update
    updatePointsTable();
    updatePolyline(); // Update the lines after movement
}

function updateEditControls(marker) {
    document.querySelector('#lat-input').value = marker.getLatLng().lat.toFixed(PRECISION);
    document.querySelector('#lng-input').value = marker.getLatLng().lng.toFixed(PRECISION);
}

function clearEditControls() {
    document.querySelector('#lat-input').value = '';
    document.querySelector('#lng-input').value = '';
}

function updateSelectedMarker() {
    if (selectedMarkerIndex === null) return;

    const marker = markers[selectedMarkerIndex];
    if (marker) {
        const newLat = parseFloat(document.querySelector('#lat-input').value);
        const newLng = parseFloat(document.querySelector('#lng-input').value);
        if (!isNaN(newLat) && !isNaN(newLng)) {
            marker.setLatLng([newLat, newLng]);
            updatePointsTable();
            map.setView([newLat, newLng]);
        } else {
            alert('Please enter valid latitude and longitude.');
        }
    }
    updatePolyline();
}

function exportToFile() {
    const pointsData = markers.map(marker => ({
        lat: marker.getLatLng().lat.toFixed(PRECISION),
        lng: marker.getLatLng().lng.toFixed(PRECISION)
    }));
    const blob = new Blob([JSON.stringify(pointsData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'points.json';
    a.click();
    URL.revokeObjectURL(url);
}

function addMarker(lat, lon, insertAfterIndex = null) {
    const markerOptions = { draggable: isEditing };
    const marker = L.marker([lat, lon], markerOptions).addTo(map);
    marker.setIcon(defaultIcon);
    marker.bindPopup(`<b>Point</b><br>Lat: ${lat.toFixed(PRECISION)}<br>Lon: ${lon.toFixed(PRECISION)}`);

    marker.on('click', () => {
        selectMarker(markers.indexOf(marker));
    });

    marker.on('dragend', () => {
        // Update
        updatePointsTable();
        updateMarkerOrderNumbers();
        updatePolyline();
    });

    let new_index = 0;

    if (insertAfterIndex !== null && insertAfterIndex >= 0 && insertAfterIndex < markers.length) {
        // Insert the new marker after the selected one
        new_index = insertAfterIndex + 1;
        markers.splice(new_index, 0, marker);
    } else {
        // Add the new marker at the end if no valid index is specified
        new_index = markers.length;
        markers.push(marker);
    }

    selectMarker(new_index); // Select newly added marker

    // Update
    updatePointsTable();
    updatePolyline();
    updateMarkerOrderNumbers();
}

// Override the map click event to add a marker after the selected one
map.on('click', function(e) {
    if (isAdding) {
        if (selectedMarkerIndex !== null) {
            addMarker(e.latlng.lat, e.latlng.lng, selectedMarkerIndex);
        } else {
            addMarker(e.latlng.lat, e.latlng.lng); // If no marker is selected, add to the end
        }
    }
});

document.querySelector('#file-upload').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            try {
                const data = JSON.parse(e.target.result);
                clearAllPoints();
                data.forEach(point => {
                    addMarker(point.lat, point.lng);
                });
            } catch (error) {
                alert('Invalid file format. Please upload a valid JSON file.');
            }
        };
        reader.readAsText(file);
    }
});

document.querySelector('#points-table').addEventListener('click', function(e) {
    const row = e.target.closest('tr');
    if (row) {
        const index = parseInt(row.dataset.index, 10);
        if (!isNaN(index)) {
            selectMarker(index);
        }
    }
});

// Drag and Drop for table rows
const tableBody = document.querySelector('#points-table tbody');

tableBody.addEventListener('dragstart', (e) => {
    e.target.classList.add('dragging');
    e.dataTransfer.setData('text/plain', e.target.dataset.index);
});

tableBody.addEventListener('dragend', (e) => {
    e.target.classList.remove('dragging');
    document.querySelectorAll('tr.drop-target-top, tr.drop-target-bottom').forEach(target => target.classList.remove('drop-target-top', 'drop-target-bottom'));
});

tableBody.addEventListener('dragover', (e) => {
    e.preventDefault();
    const draggingRow = document.querySelector('tr.dragging');
    const dropTargetRow = e.target.closest('tr');
    if (!dropTargetRow || dropTargetRow === draggingRow) return;

    const draggingIndex = parseInt(draggingRow.dataset.index, 10);
    const targetIndex = parseInt(dropTargetRow.dataset.index, 10);

    document.querySelectorAll('tr.drop-target-top, tr.drop-target-bottom').forEach(target => target.classList.remove('drop-target-top', 'drop-target-bottom'));

    if (draggingIndex < targetIndex) {
        dropTargetRow.classList.add('drop-target-bottom');
    } else if (draggingIndex > targetIndex) {
        dropTargetRow.classList.add('drop-target-top');
    }
});

tableBody.addEventListener('dragleave', (e) => {
    const dropTargetRow = e.target.closest('tr');
    if (dropTargetRow) {
        dropTargetRow.classList.remove('drop-target-top', 'drop-target-bottom');
    }
});

tableBody.addEventListener('drop', (e) => {
    e.preventDefault();
    const fromIndex = parseInt(e.dataTransfer.getData('text/plain'), 10);
    const toIndex = parseInt(e.target.closest('tr').dataset.index, 10);

    if (fromIndex !== toIndex && !isNaN(fromIndex) && !isNaN(toIndex)) {
        // Reorder markers array
        const marker = markers.splice(fromIndex, 1)[0];
        markers.splice(toIndex, 0, marker);
        
        // Update the selection index
        if (selectedMarkerIndex === fromIndex) {
            selectedMarkerIndex = toIndex;
        } else if (fromIndex < selectedMarkerIndex && toIndex >= selectedMarkerIndex) {
            selectedMarkerIndex--;
        } else if (fromIndex > selectedMarkerIndex && toIndex <= selectedMarkerIndex) {
            selectedMarkerIndex++;
        }

        selectMarker(selectedMarkerIndex);

        // Update
        updatePointsTable();
        updatePolyline();
    }

    document.querySelectorAll('tr.drop-target-top, tr.drop-target-bottom').forEach(target => target.classList.remove('drop-target-top', 'drop-target-bottom'));
});

// Update the lines after dragging rows
function updatePolyline() {
    // Remove existing polyline and arrow
    if (polyline) {
        map.removeLayer(polyline);
        polyline = null; 
    }
    
    if (markers.length > 1) {
        const latlngs = markers.map(marker => marker.getLatLng());

        // Create a new polyline connecting the points
        polyline = L.polyline(latlngs, { color: COLOR3 }).addTo(map);
    }
}

// Send data to the server
document.getElementById('upload-mission-btn').addEventListener('click', function() {
    const ipAddress = document.getElementById('ip-address').value;
    const port = document.getElementById('port').value;
    const height = document.getElementById('height').value;

    if (markers.length === 0) {
        alert('No points to upload.');
        return;
    }

    // Convert markers data to JSON format
    const data = markers.map(marker => {
        const latlng = marker.getLatLng();
        return { lat: latlng.lat, lng: latlng.lng };
    });

    const dataJson = JSON.stringify({
        data: data,
        ip: ipAddress,
        port: port,
        height: height
    });

    // Send the data to the server
    fetch('http://localhost:8001/upload', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: dataJson
    })
    .then(response => {
        if (response.ok) {
            alert('Mission uploaded successfully.');
        } else {
            alert(`Failed to upload data. Server responded with status code ${response.status}.`);
        }
    })
    .catch(error => {
        alert(`Failed to upload data. Error: ${error}`);
    });
});