let map;
let markers = [];


function DefaultMap(){
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: { 
            lat: -26.1076,
            lng: 28.0567 
        },
    });
}

const addressInput = document.getElementById('address-input');
const errorDiv = document.getElementById('error-message');

addressInput.addEventListener('input', () => {
    // If the error message is currently visible, hide it
    if (errorDiv.style.display === "block") {
        errorDiv.style.display = "none";
        errorDiv.innerText = "";
    }
});


document.getElementById('search-btn').addEventListener('click', async () => {

    const address = addressInput.value;
    const type = document.getElementById('place-type').value;

    if (!address) return alert("Please enter an address!");

    try {
        const response = await fetch(`/api/nearby?address=${encodeURIComponent(address)}&type=${type}`);
        const data = await response.json();

        if (!response.ok) {
            errorDiv.innerText = data.message || "Location not found. Please try again.";
            errorDiv.style.display = "block";
            return;
        }

        if (data.results) {
            updateUI(data.results, data.location);
        }
    } catch (error) {
        console.error("API Error:", error);
        errorDiv.innerText = "Connection error. Is the Flask server running?";
        errorDiv.style.display = "block";
    }
});


function updateUI(places, location) {
    // Clear markers
    markers.forEach(m => {
        console.log("Current Marker:", m);
        m.setMap(null)
    });
    markers = [];

    // Reset list
    const list = document.getElementById('place-list');
    list.innerHTML = "";

    // Set map center
    map.setCenter(location);
    map.setZoom(14);

    places.forEach(place => {
        // Add Marker
        const marker = new google.maps.Marker({
            position: place.geometry.location,
            map: map,
            title: place.name
        });

        markers.push(marker);

        // Add to List
        const li = document.createElement('li');
        li.className = "place-list";
        li.innerHTML = `<strong>${place.name}</strong><br>${place.vicinity}<br>Rating: ${place.rating || 'N/A'}`;
        list.appendChild(li);
    });
}

window.onload = DefaultMap;
